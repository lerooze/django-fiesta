from django.db.models import Q
from fiesta.core import status
from fiesta.core import constants
from fiesta.parsers import XMLParser
from fiesta.core import patterns
from dataclasses import asdict
from typing import Iterable
from datetime import datetime, date, timedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from fiesta.utils.translation import get_language
from django.utils import translation
from fiesta.settings import api_settings
from django.apps import apps
from django.db import transaction
from decimal import Decimal
from rest_framework.exceptions import ParseError 
from .base import field, FiestaDataclass, EmptyDataclass

class CommonDataclass(FiestaDataclass):

    class Meta:
        namespace_key = 'common'

class BaseDataclass(FiestaDataclass):

    class Meta:
        app = 'base'

class RegistryDataclass(FiestaDataclass):

    class Meta:
        namespace_key = 'registry'

class StringDataclass(FiestaDataclass):
    text: str = field(is_text=True)

class TextDataclass(StringDataclass):

    lang: str = field(namespace_key='xml', default='en')

    class Meta:
        app = 'common'
        model_name = 'text'

    def process_prevalidate(self):
        if not self.lang in settings.LANGUAGES: 
            self._context.result.status_message.update(
                'Failure',
                status.FIESTA_2501_NOT_SUPPORTED_LANGUAGE
            )

    def process_premake(self):
        return self._meta.model.get_or_create(
            polymorphic_obj=self._wrapper._obj,
            text=self.text,
            text_type=self._field.name,
            language=self.lang
        )

    @classmethod
    def generate_many(cls, related_obj, field):
        for obj in cls._meta.model.get_polymorphic(related_obj, field.name):
            for lang in settings.LANGUAGES:
                yield cls(
                    text=getattr(obj, f'text_{lang}', None),
                    lang=lang
                )

class SimpleStringDataclass(FiestaDataclass):
    value = field(is_text=True)


class RefDataclass(FiestaDataclass):
    agency_id: str = field(localname='agencyID', is_attribute=True,
                           forward=True, forward_accesor='agency__object_id')
    maintainable_parent_id: str = field(localname='maintainableParentID', is_attribute=True)
    maintainable_parent_version: str = field(is_attribute=True)
    container_id: str = field(localname='containerID', is_attribute=True)
    object_id: str = field(localname='id', is_attribute=True)
    version: str = field(is_attribute=True)
    local: bool = field(is_attribute=True)
    cls: str= field(localname='class', is_attribute=True)
    package: str = field(is_attribute=True)

    def finalize_object_serialization(self, django_obj):
        object_name = django_obj._meta.object_name
        if object_name == 'codelist':
            self.cls = 'Codelist'
            self.package = 'codelist'
        elif object_name == 'conceptscheme':
            self.cls = 'ConceptScheme'
            self.package = 'conceptscheme'

class ReferenceDataclass(CommonDataclass):
    ref: RefDataclass = field()
    urn: str = field(localname='URN')

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.dref = self._urn_to_ref() or self.ref

    def make_maintainable_urn(self):
        if self.urn: return self.urn
        d = self.dref
        urn = f'urn:sdmx:infomodel.{d.package}.{d.cls}={d.agency}:{d.object_id}({d.version})' 
        return urn

    def _urn_to_ref(self):
        if not self.urn: return
        ref = RefDataclass()
        lurn, rurn = self.urn.split('=')
        lurn = lurn.split(':')[-1]
        _, ref.package, ref.cls = lurn.split('.')
        ref.agency_id, remaining = rurn.split(':')
        match = patterns.MAINTAINABLE.match(remaining)
        if match:
            ref.object_id = match.group('object_id')
            ref.version = match.group('version') or '1.0'
        else:
            match = patterns.PARENTABLE.match(remaining)
            ref.object_id = match.group('object_id')
            ref.version = match.group('version') or '1.0'
            ref.maintainable_parent_id = match.group('maintainable_parent_id')
            ref.maintainable_parent_version = match.group('maintainable_parent_version')
            ref.container_id = match.group('container_id')
        return ref

class SimpleStringContactDataclass(SimpleStringDataclass):

    def process_premake(self):
        return self._meta.model.get_or_create(
            value=self.value,
            contact=self._wrapper._obj
        )

class TelephoneDataclass(SimpleStringContactDataclass):

    class Meta:
        app = 'base'
        model_name = 'telephone'

class FaxDataclass(SimpleStringContactDataclass):

    class Meta:
        app = 'base'
        model_name = 'fax'

class X400Dataclass(SimpleStringContactDataclass):

    class Meta:
        app = 'base'
        model_name = 'x400'

class URIDataclass(SimpleStringContactDataclass):

    class Meta:
        app = 'base'
        model_name = 'uri'

class EmailDataclass(SimpleStringContactDataclass):

    class Meta:
        app = 'base'
        model_name = 'email'

class BaseContactDataclass(FiestaDataclass):

    name: Iterable[TextDataclass] = field(namespace_key='common')
    department: Iterable[TextDataclass] = field()
    role: Iterable[TextDataclass] = field()
    telephone: Iterable[TelephoneDataclass] = field()
    fax: Iterable[FaxDataclass] = field()
    x400: Iterable[X400Dataclass] = field()
    uri: Iterable[URIDataclass] = field(localname='URI')
    email: Iterable[EmailDataclass] = field()

    class Meta:
        app = 'base'
        model_name = 'Contact'
        namespace_key = 'message'

class ContactDataclass(BaseContactDataclass):

    def process_prevalidate(self):
        if not self.email:
            self._context.result.status_message.update(
                'Warning', 
                status.FIESTA_2404_NO_EMAIL
            )
            self._stop= True

    def process_premake(self):
        username = list(self.email)[0]
        obj, self._new_user = self._meta.model.objects.get_or_create(
            username, self._wrapper)
        return obj

    def process_postmake(self, obj):
        if self._new_user:
            obj.send_password_reset_email(self._context.request)
        obj.save()
        return obj

class HeaderContactDataclass(BaseContactDataclass):

    def process_prevalidate(self):
        # Checking that contact has an email
        if not self.email:
            self._context.result.status_message.update(
                'Warning',
                status.FIESTA_1002_HEADER_CONTACT_EMAIL_NOT_FOUND,
            )
            obj = None
        else: 
            username = self.email[0]
            try:
                obj = self._meta.model.objects.get(username=username)
            except self._meta.model.DoesNotExist:
                self._context.result.status_message.update(
                    'Warning',
                    status.FIESTA_1004_CONTACT_NOT_REGISTERED,
                    f'Username: {username}'
                )
            else:
                # Checking that user is a member of Organisation
                if obj.organisation != self._wrapper._obj:
                    self._context.result.status_message.update(
                        'Warning',
                        status.FIESTA_1003_USER_NOT_IN_ORGANISATION,
                        f'Username {username}, organisation {self._wrapper._obj}'
                    )
        self._obj = obj 

    def process_premake(self):
        self._stop = True
        return self._obj

class PartyDataclass(FiestaDataclass):

    name: Iterable[TextDataclass] = field(namespace_key='common')
    contact: Iterable[HeaderContactDataclass] = field()
    object_id: str = field(is_attribute=True, localname='id')

    class Meta:
        app = 'base'
        model_name = 'Organisation'
        namespace_key = 'message'

    def process_prevalidate(self):
        # Checking that receiver organisation exists
        try:
            obj = self._meta.model.objects.get(
                object_id=self.object_id)
        except self._meta.model.Organisation.DoesNotExist:
            self._context.result.status_message.update(
                'Warning',
                status.FIESTA_1001_HEADER_ORGANISATION_NOT_REGISTERED,
                f'[organisation id: {self.object_id}]'
            )
            obj = None
        self._obj = obj 

    def process_premake(self):
        self._skip_save = True
        return self._obj

    def wsrest_party(self, registration):
        if isinstance(registration.user, AnonymousUser):
            self.object_id='not_supplied'
            return
        contact = HeaderContactDataclass(email=[registration.user.username])
        receiver = registration.user.contact.organisation
        self.object_id = receiver.object_id
        self.contact = [contact]

class SenderDataclass(PartyDataclass):
    timezone: str = field(namespace_key='message')

    def wsrest_sender(self):
        self.object_id = api_settings.DEFAULT_SENDER_ID 

class PayloadStructureDataclass(CommonDataclass):
    provision_agreement: ReferenceDataclass = field()
    structure_usage: ReferenceDataclass = field()
    structure: ReferenceDataclass = field()
    structure_id: str = field(is_attribute=True, localname='structureID')
    schema_url: str = field(is_attribute=True, localname='schemaURL')
    namespace: str = field(is_attribute=True)
    dimension_at_observation: str = field(is_attribute=True)
    explicit_measures: str = field(is_attribute=True)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)

class HeaderDataclass(FiestaDataclass):
    object_id: str = field(localname='ID')
    test: bool = field(default=False)
    prepared: datetime = field()
    sender: SenderDataclass = field()
    receiver: PartyDataclass = field()
    name: Iterable[TextDataclass] = field(namespace_key='common')
    structure: Iterable[PayloadStructureDataclass] = field()
    data_provider: ReferenceDataclass = field()
    data_set_action: str = field()
    data_set_id: str = field(localname='DataSetID')
    extracted: datetime = field()
    reporting_begin: str = field()
    reporting_end: str = field()
    embargo_date: datetime = field()
    source: str = field()

    class Meta:
        app = 'registry'
        model_name = 'Submission'
        namespace_key = 'message'

    def _header_to_bogus_reference(self):
        ref = RefDataclass(
            agency_id='MAIN',
            object_id='HEADER',
            version='1.0',
            cls='Agency',
            package='base'
        )
        reference =  ReferenceDataclass(ref=ref)
        reference.durn = reference.make_maintainable_urn()
        return reference

    def to_submission_result(self):
        reference = self._header_to_bogus_reference()
        submitted_structure = SubmittedStructureDataclass(
            maintainable_object=reference, 
        )
        submission_result = submitted_structure.to_result()
        return submission_result

    def process_prevalidate(self):
        self._context.result = self._context.get_or_add_result(self.to_submission_result())

    def process_postmake(self, obj):
        super().process_postmake(obj)
        obj = self._meta.model.objects.create(
            log=self._context.log,
            object_id=self.object_id,
            test=self.test,
            prepared=self.prepared,
            sender=self._sender,
            receiver=self._receiver,
        )
        obj.sender_contacts.add(*self.sender._contact)
        obj.receiver_contacts.add(*self.receiver._contact)
        self._sid = transaction.savepoint()
        return obj

    def to_response(self):
        header = HeaderDataclass(
            object_id=self._obj.id,
            test=self.test,
            prepared=datetime.now(),
            sender=self.receiver,
            receiver=self.sender,
        )
        if self.test:
            transaction.savepoint_rollback(self._sid)
        return header 

    def to_structure(self, log):
        self.object_id=log.restful_query.id,
        self.test=False,
        self.prepared=log.prepared,
        self.sender=SenderDataclass().wsrest_sender(),
        self.receiver=PartyDataclass().wsrest_party(log.restful_query),

class AnnotationDataclass(FiestaDataclass):
    annotation_title: str = field(is_text=True)
    annotation_type: str = field(is_text=True)
    annotation_url: str = field(is_text=True, localname='AnnotationURL')
    annotation_text: Iterable[TextDataclass] = field()
    object_id: str = field(is_attribute=True, localname='id')

    class Meta:
        app = 'common'
        model_name = 'Annotation'
        namespace_key = 'common'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            object_id=self.object_id,
            annotation_title=self.annotation_title,
            annotation_type=self.annotation_type,
            annotation_url=self.annotation_url,
            annotable_object=self._wrapper._obj,
        )
        return obj

    @classmethod
    def generate_many(cls, related_obj, *args, **kwargs):
        for obj in cls._meta.model.get_polymorphic(related_obj):
            yield cls(obj, complain=False)

class AnnotableDataclass(CommonDataclass):
    annotations: Iterable[AnnotationDataclass] = field(namespace_key='common')

class IdentifiableDataclass(AnnotableDataclass):
    object_id: str = field(is_attribute=True, localname='id')
    urn: str = field(is_attribute=True)
    uri: str = field(is_attribute=True)

    def finalize_object_serialization(self):
        self.urn = self.make_urn()
        self.uri = self.make_uri()

    def make_urn(self):
        pass

    def make_uri(self):
        pass

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if not obj.object_id:
            obj.object_id = self.object_id
        return obj

class NameableDataclass(IdentifiableDataclass):
    name: Iterable[TextDataclass] = field(namespace_key='common')
    description: Iterable[TextDataclass] = field(namespace_key='common')

class VersionableDataclass(NameableDataclass):
    version: str = field(is_attribute=True, default='1.0')
    valid_from: datetime = field(is_attribute=True)
    valid_to: datetime = field(is_attribute=True)

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if not obj.version:
            obj.version = self.version
        if not obj.valid_from:
            obj.valid_from = self.valid_from
        if not obj.valid_to:
            obj.valid_to = self.valid_to
        return obj

class MaintainableDataclass(VersionableDataclass):
    agency_id: str = field(is_attribute=True, localname='agencyID',
                           forward=True, forward_accesor='agency__object_id')
    is_final: bool = field(is_attribute=True, default=False)
    is_external_reference: bool = field(is_attribute=True, default=False)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)

    def make_structure_url(self):
        resource = constants.CLASS2RESOURCE(self._meta.name)[0]
        return f'http://www.fiesta.org/{resource}/{self.agency_id}/{self.version}'

    @classmethod
    def generate_many(cls, query):
        for obj in cls._meta.model.objects.filter(query):
            yield cls(obj)

    @classmethod
    def make_root_query(cls, context):
        kwargs = {}
        if context.query.resource_id != 'all':
            kwargs['object_id'] = context.query.resource_id
        if context.query.agency_id != 'all':
            kwargs['agency__object_id'] = context.query.agency_id
        if context.query.version == 'latest':
            kwargs['latest'] = True
        elif context.query.version != 'all':
            kwargs['version'] = context.query.version
        return Q(**kwargs) 

    @classmethod
    def make_other_query(cls, sibling_cls, base):
        return Q()

    @classmethod
    def _make_query_args(cls, context, depth):
        references = context.query.references
        qrs = context.queries
        if not depth:
            qrs[cls] = qrs[cls] | cls.make_root_query(context) 
        depth += 1
        if references in ['children', 'parentsandsiblings'] and depth == 1:
            for cld_cls in cls._meta.children:
                qrs[cld_cls] = qrs[cld_cls] | cld_cls.make_other_query(cls, qrs[cld_cls])
        elif references in ['descendants', 'all'] and depth >= 1:
            for cld_cls in cls._meta.children:
                qrs[cld_cls] = qrs[cld_cls] | cld_cls.make_other_query(cls, qrs[cld_cls])
            for cld_cls in cls._meta.children:
                cld_cls._make_query_args(context, depth)
        elif references in constants.RESOURCES:
            for item in constants.RESOURCE2MAINTAINABLE[references]:
                cld_cls = cls._meta.select_child(item)
                if not cld_cls: continue
                qrs[cld_cls] = qrs[cld_cls] | cld_cls.make_other_query(cls, qrs[cld_cls])
        if references in ['parents', 'parentsandsiblings', 'all'] and depth == 1:
            for parent in cls._meta.parents:
                qrs[parent] = qrs[parent] | parent.make_other_query(cls, qrs[parent])

    def _to_element_as_stub(self, class_meta, detail, resource):
        """Returns True if element should be rendered as stub."""
        return (
            (detail == 'allstubs') 
            or
            ((detail == 'referencestubs') and 
             (resource not in class_meta.resources))
        )

    def _get_maintainable(self, structures):
        maintainable_wrapper = self._field.name
        structure_wrapper_name = self._wrapper._wrapper._context.underscore_name
        structure_wrapper = getattr(structures, structure_wrapper_name, None)
        try:
            obj = list(getattr(structure_wrapper, maintainable_wrapper))[0]
        except (IndexError, KeyError, AttributeError):
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2202_PULLED_NO_CONTENT_STRUCTURE) 
        else:
            return obj

    def get_external(self):
        location = self.structure_url
        if not location:
            self._context.result.status_message.update(
                'Failure',
                status.FIESTA_2103_SOAP_PULLING_NOT_IMPLEMENTED
            ) 
            return
        message = XMLParser().get(location)
        if not isinstance(message, StructureDataclass):
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2201_PULLED_NOT_STRUCTURE
            ) 
            return
        obj = self._get_maintainable(message.structures)
        if not obj: return
        obj_stub = (obj.agency_id, obj.object_id, obj.version) 
        self_stub = (self.agency_id, self.object_id, self.version)
        if obj_stub != self_stub:
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2203_PULLED_UNEXPECTED_CONTENT) 
            return
        return obj

    def to_reference(self):
        ref = RefDataclass(
            agency_id=self.agency_id,
            object_id=self.object_id,
            version=self.version,
            cls=self._meta.class_name,
            package=self._meta.app
        )
        reference =  ReferenceDataclass(ref=ref)
        reference.durn = reference.make_maintainable_urn()
        return reference

    def to_submission_result(self):
        reference = self.to_reference()
        submitted_structure = SubmittedStructureDataclass(
            maintainable_object=reference, 
            action=self._wrapper._wrapper.action, 
            external_dependencies=self._wrapper._wrapper.external_dependencies
        )
        submission_result = submitted_structure.to_result()
        submission_result._wrapper = self._wrapper._wrapper._obj
        return submission_result

    def process_prevalidate(self):
        self._context.result = self.get_or_add_result(self.to_submission_result())
        model = apps.get_model('base', 'Organisation')
        try:
            self.agency = model.objects.get(object_id=self.agency_id)
        except model.DoesNotExist:
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2403_AGENCY_NOT_REGISTERED,
            )
            self._inner_stop = True

    def process_premake(self):
        if self.is_external_reference:
            sdmxobj = self.get_external()
            if not sdmxobj:
                self._stop = True
                return
            self = sdmxobj
        obj, created = self._meta.model.objects.get_or_create(
            agency=self.agency,
            object_id=self.object_id,
            version=self.version
        )
        self._meta.models.objects.reset_latest(created, self)
        return obj 

    def process_validate(self, obj):
        action = self._context.action
        if action in ['Replace', 'Delete']:
            if obj.is_final:
                self._context.result.status_message.update(
                    'Failure',
                    status.FIESTA_2101_MODIFICATION_NOT_ALLOWED
                ) 
                self._stop = True
            else:
                obj.delete()
                if action == 'Delete':
                    self._context.result.status_message.update(
                        'Success',
                    ) 
                    self._stop = True

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if not obj.is_final:
            obj.is_final = self.is_final
        self._context.result.status_message.update('Success')
        self._context.maintainable = obj
        self._context.result.process(context=self._context)
        return obj

class ItemSchemeDataclass(MaintainableDataclass):
    is_partial: bool = field(is_attribute=True, default=False)

class StructuresItemsDataclass(FiestaDataclass):

    class Meta:
        namespace_key = 'structure'

    def _make_query_args(self, context):
        for f in self._meta.fields:
            if f.name not in context.maintainable_query_field_names:
                continue
            maintainable_type = f.type.__args__[0]
            maintainable_type._make_query_args(context, depth=0)

    def retrieve_restful(self, context):
        for f in self._meta.fields:
            maintainable_type = f.type.__args__[0]
            if maintainable_type not in context.queries_kwargs: continue
            query = context.queries_kwargs[maintainable_type]
            setattr(self, f.name, maintainable_type.generate_many(query))

class BaseItemDataclass(NameableDataclass):
    parent: ReferenceDataclass = field(namespace_key='common', forward=True)

class ItemDataclass(BaseItemDataclass):

    @classmethod
    def generate_many(cls, related_obj, specifier, *args, **kwargs):
        for obj in getattr(related_obj, specifier):
            yield cls(obj=obj)

    def get_parent(self, parent_id):
        return self._meta.model.objects.get(object_id=parent_id,
                                            wrapper=self._wrapper._obj)

    def process_prevalidate(self):
        parent_obj = None
        if self.parent:
            parent_id = self.parent.dref.object_id
            try:
                parent_obj = self.get_parent(parent_id)
            except self._meta.model.DoesNotExist:
                self._context.result.status_message.update(
                    'Warning',
                    status.FIESTA_2401_NOT_FOUND_PARENT
                )
        self._parent_obj = parent_obj

    def process_premake(self):
        return self._meta.model.get_or_create(
            object_id=self.object_id,
            wrapper=self._wrapper._obj,
            parent=self._parent_obj
        )

class ManyToManyItemDataclass(ItemDataclass):

    def get_parent(self, parent_id):
        return self._meta.model.objects.get(object_id=parent_id)

    def process_prevalidate(self):
        super().process_prevalidate()
        if self._parent_obj:
            if self._wrapper._obj not in self._parent_obj.wrappers:
                self._context.status_message.update(
                    'Warning',
                    status.FIESTA_2405_PARENT_NOT_IN_SCHEME
                )
    
class OrganisationDataclass(ManyToManyItemDataclass):
    contact: Iterable[ContactDataclass] = field()

    class Meta:
        app = 'base'
        model_name = 'organisation'
        namespace_key = 'structure'

class AgencyDataclass(OrganisationDataclass):
    pass

class DataProviderDataclass(OrganisationDataclass):
    pass

class DataConsumerDataclass(OrganisationDataclass):
    pass

class OrganisationUnitDataclass(OrganisationDataclass):
    pass

class OrganisationSchemeDataclass(ItemSchemeDataclass):

    class Meta:
        app = 'base'
        model_name = 'organisationscheme'
        namespace_key = 'structure'

class AgencySchemeDataclass(OrganisationSchemeDataclass):
    agency: Iterable[AgencyDataclass] = field() 

    @classmethod
    def make_root_query(cls, context):
        root = super().make_root_query(context)
        root_args = dict(*root.children)
        resource_id = root_args.get('object_id')
        if resource_id and resource_id != 'AGENCIES':
            raise ParseError('The resourceID of an agencyscheme query must be equal to AGENCIES if set')
        else: root = root & Q(object_id='AGENCIES')
        return root

class DataConsumerSchemeDataclass(OrganisationSchemeDataclass):
    data_consumer: Iterable[DataConsumerDataclass] = field(namespace_key='structure', related_name='organisations') 

    @classmethod
    def make_root_query(cls, context):
        root = super().make_root_query(context)
        root_args = dict(*root.children)
        resource_id = root_args.get('object_id')
        if resource_id and resource_id != 'DATA_CONSUMERS':
            raise ParseError('The resourceID of an dataconsumerscheme query must be equal to DATA_CONSUMERS if set')
        else: root = root & Q(object_id='DATA_CONSUMERS')
        return root

class DataProviderSchemeDataclass(OrganisationSchemeDataclass):
    data_provider: Iterable[DataProviderDataclass] = field(namespace_key='structure', related_name='organisations') 

    @classmethod
    def make_root_query(cls, context):
        root = super().make_root_query(context)
        root_args = dict(*root.children)
        resource_id = root_args.get('object_id')
        if resource_id and resource_id != 'DATA_PROVIDERS':
            raise ParseError('The resourceID of a dataproviderscheme query must be equal to DATA_PROVIDERS if set')
        else: root = root & Q(object_id='DATA_PROVIDERS')
        return root

class OrganisationUnitSchemeDataclass(OrganisationSchemeDataclass):
    organisation_unit: Iterable[OrganisationUnitDataclass] = field(namespace_key='structure', related_name='organisations') 

class OrganisationSchemesDataclass(StructuresItemsDataclass):
    agency_scheme: Iterable[AgencySchemeDataclass] = field()
    data_consumer_scheme: Iterable[DataConsumerSchemeDataclass] = field()
    data_provider_scheme: Iterable[DataProviderSchemeDataclass] = field()
    organisation_unit_scheme: Iterable[OrganisationUnitSchemeDataclass] = field()

    class Meta:
        app = 'base'
        namespace_key = 'structure'

class CodeDataclass(ItemDataclass):
    class Meta:
        app = 'codelist'
        model_name = 'code'
        namespace_key = 'structure'

class CodelistDataclass(ItemSchemeDataclass):
    code: Iterable[CodeDataclass] = field() 

    class Meta:
        app = 'codelist'
        model_name = 'codelist'
        namespace_key = 'structure'

    @classmethod
    def make_other_query(cls, sibling_cls, base):
        base = super().make_other_query(sibling_cls, base)
        if sibling_cls == ConceptSchemeDataclass:
            base = base | Q(enumerations__concepts__wrapper__in=sibling_cls.objects.filter(base))
        return base

class CodelistsDataclass(StructuresItemsDataclass):
    codelist: Iterable[CodelistDataclass] = field(namespace_key='structure')

class FormatDataclass(FiestaDataclass):
    text_type: str = field(is_attribute=True, default='String')
    is_sequence: bool = field(is_attribute=True)
    interval: Decimal = field(is_attribute=True)
    start_value: Decimal = field(is_attribute=True)
    end_value: Decimal = field(is_attribute=True)
    time_interval: timedelta = field(is_attribute=True)
    start_time: str = field(is_attribute=True)
    end_time: str = field(is_attribute=True)
    min_length: int = field(is_attribute=True)
    max_length: int = field(is_attribute=True)
    min_value: Decimal = field(is_attribute=True)
    max_value: Decimal = field(is_attribute=True)
    decimals: Decimal = field(is_attribute=True)
    pattern: str = field(is_attribute=True)
    is_multi_lingual: bool = field(is_attribute=True)
   
    class Meta:
        app = 'common'
        model_name = 'format'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            **asdict(self)
        )
        return obj

class RepresentationDataclass(FiestaDataclass):
    text_format: FormatDataclass = field(forward=True)
    enumeration: ReferenceDataclass = field(forward=True)
    enumeration_format: FormatDataclass = field(forward=True)

    class Meta:
        app = 'common' 
        model_name = 'representation'
        namespace_key = 'common'

            
    def process_postmake(self):
        enumeration = self.enumeration
        if enumeration:
            ref = enumeration.dref
            codelist_model = apps.get_model('codelist', 'Codelist')
            try:
                codelist_obj = codelist_model.objects.get(
                    agency_id=ref.agency_id,
                    object_id=ref.object_id,
                    version=ref.version
                )
            except codelist_model.DoesNotExist:
                self._context.status_message.update(
                    'Warning',
                    status.FIESTA_2402_REPRESENTATION_CODELIST_NOT_REGISTERED
                )
                return
        obj, _ = self._meta.model.objects.get_or_create(
            text_format=self.m_text_format,
            enumeration=codelist_obj,
            enumeration_format=self.m_enumeration_format)
        return obj

class ISOConceptReferenceDataclass(FiestaDataclass):
    concept_agency: str = field()
    concept_scheme_id: str = field(localname='ConceptSchemeID')
    concept_id: str = field(localname='ConceptID')

    class Meta:
        app = 'conceptscheme'
        model_name = 'isoconceptreference'
        namespace_key = 'structure'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            **asdict(self))
        return obj

class ConceptDataclass(ItemDataclass):
    core_representation: RepresentationDataclass = field(forward=True)
    iso_concept_reference: ISOConceptReferenceDataclass = field(localname='ISOConceptReference', forward=True)

    class Meta:
        app = 'conceptscheme'
        model_name = 'concept'
        namespace_key = 'structure'

    def process_postmake(self, obj):
        super().process_postmake(obj)
        if not obj.core_representation:
            obj.core_representation = self._core_representation
        if not obj.iso_concept_reference:
            obj.iso_concept_reference = self._iso_concept_reference
        obj.save()
        return obj

class ConceptSchemeDataclass(ItemSchemeDataclass):
    concept: Iterable[ConceptDataclass] = field() 

    class Meta:
        app = 'conceptscheme'
        model_name = 'conceptscheme'
        namespace_key = 'structure'
        children_names = 'CodelistDataclass'

class ConceptsDataclass(StructuresItemsDataclass):
    concept_scheme: Iterable[ConceptSchemeDataclass] = field()

class StructuresDataclass(FiestaDataclass):
    organisation_schemes: OrganisationSchemesDataclass = field()
    # dataflows: DataflowsDataclass = field(namespace_key='registry')
    # metadataflows: MetadataflowsDataclass = field(namespace_key='registry')
    # category_schemes: CategorySchemesDataclass = field(namespace_key='registry')
    # categorisations: CategorisationsDataclass = field(namespace_key='registry')
    codelists: CodelistsDataclass = field()
    # hierarchical_codelists: HierarchicalCodelistsDataclass = field(namespace_key='registry')
    concepts: ConceptsDataclass = field()
    # metadata_structures: MetadataStructuresDataclass = field(namespace_key='registry')
    # data_structures: DataStructuresDataclass = field(namespace_key='registry')
    # structure_sets: StructureSetsDataclass = field(namespace_key='registry')
    # reporting_taxonomies: ReportingTaxonomiesDataclass = field(namespace_key='registry')
    # processes: ProcessesDataclass = field(namespace_key='registry')
    # constraints: ConstraintsDataclass = field(namespace_key='registry')
    # provision_agreements: ProvisionAgreementsDataclass = field(namespace_key='registry')

    class Meta:
        namespace_key = 'structure'

    def retrieve_restful(self, context):
        for f in self._meta.fields:
            if f.name not in context.structrures_field_names: continue
            f.type._make_query_args(context)
        for f in self._meta.fields:
            if f.name not in context.all_structures: continue
            value = f.type()
            value.retrieve_restful(context)
            setattr(self, f.name, value)


class FooterMessageDataclass(FiestaDataclass):

    text: Iterable[TextDataclass] = field(namespace_key='common')
    code: str = field(is_attribute=True)
    severity: str = field(is_attribute=True)

    class Meta:
        namespace_key = 'common'

class FooterDataclass(FiestaDataclass):
    message: Iterable[FooterMessageDataclass] = field()

    class Meta:
        namespace_key = 'footer'

    def process_prevalidate(self):
        errors = (message for message in self.message if message.severity in
                  ['Error', 'Warning'])
        for message in self.message:
            if message.severity != 'Error': pass
            self._context.result.status_message.update(
                'Failure',
                status.FIESTA_1101_NOT_PROCESSED_FOOTER_ERRORS,
            )

        if errors:
            self.append_error('461', errors=', '.join(errors))
            self._stop = True

class BaseSDMXMessageDataclass(FiestaDataclass):
    header: HeaderDataclass = field()
    footer: FooterDataclass = field(namespace_key='footer')

    class Meta:
        namespace_key = 'message'

class StructureDataclass(BaseSDMXMessageDataclass):
    structures: StructuresDataclass = field()

    def to_request(self):
        submit_structure_request = SubmitStructureRequestDataclass(
            structures=self.structures,
            action='Replace',
            external_dependencies=True
        ) 
        sender = SenderDataclass(object_id='ECB')
        receiver = PartyDataclass(object_id='FIESTA')
        header = HeaderDataclass(
            object_id='FIESTA_MSG_ID_000001',
            test=False,
            prepared=datetime.now(),
            sender=sender,
            receiver=receiver
        )
        return RegistryInterfaceSubmitStructureRequestDataclass(
            header=header,
            submit_structure_request=submit_structure_request
        )

    def retrieve_restful(self, context):
        self.structures = StructuresDataclass().retrieve_restful(context)
        self.header = HeaderDataclass().to_structure(context.log.restful_query)

class SubmittedStructureDataclass(RegistryDataclass):
    maintainable_object: ReferenceDataclass = field()
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True)

    def to_result(self):
        new_self = self.__class__(
            maintainable_object=self.maintainable_object,
            action=self.action or self._context.action,
            external_dependencies=self.external_dependencies or self._context.external_dependencies
        )
        return SubmissionResultDataclass(
            submitted_structure=new_self,
            status_message=StatusMessageDataclass()
        )

class SubmitStructureRequestDataclass(RegistryDataclass):
    structure_location: str = field() 
    structures: StructuresDataclass = field()
    submitted_structure: Iterable[SubmittedStructureDataclass] = field()
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True) 

    class Meta:
        app = 'registry'
        model = 'submitstructurerequest'
        namespace_key = 'registry'

    def process_prevalidate(self):
        if not self.structures:
            loc = self.structure_location
            message = XMLParser().get(loc)
            if not isinstance(message, StructureDataclass):
                self._context.result.status_message.update(
                    'Failure',
                    status.FIESTA_2201_PULLED_NOT_STRUCTURE
                )
        if self._context.result.status_message.status == 'Failure':
            self._stop = True 
        self.structures = message.structures
        self._context.action = self.action
        self._context.external_dependencies = self.external_dependencies

    def process_premake(self):
        obj = self._meta.model.objects.create(
            submission=self._wrapper.m_header,
            structure_location=self.structure_location,
            action=self.action,
            external_dependencies=self.external_dependencies
        )
        for submitted_structure in self.submitted_structure:
            self._context.get_or_add_result(submitted_structure.to_result())
        return obj

    def to_response(self):
        return SubmitStructureResponseDataclass(
            submission_result = self._context.generate_result()
        )

class StatusMessageTextDataclass(TextDataclass):
    text: Iterable[TextDataclass] = field(namespace_key='common')
    code: str = field(is_attribute=True)

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            code = self.code 
        )
        return obj

class StatusMessageDataclass(RegistryDataclass):
    message_text: Iterable[StatusMessageTextDataclass] = field()
    status: str = field(is_attribute=True)

    class Meta:
        app = 'registry'
        model_name = 'statusmessage'
        namespace_key = 'registry'

    def process_premake(self):
        obj = self._meta.model.objects.create(
            status=self.status
        )
        return obj

    def update(self, status, message=None, detail=None):
        if self.status == 'Failure':
            pass
        elif self.status == 'Warning':
            if status == 'Failure': self.status = 'Failure'
            else: pass
        else:
            self.status = status
        if not message: return
        self.message_text = self.message_text or []
        language = (get_language(self._context.request.LANGUAGE_CODE))
        with translation.override(language):
            text_entry = ': '.join(filter(None, [translation.gettext(message.text), detail]))
            text = [TextDataclass(language, text_entry)]
        self.message_text.append(StatusMessageTextDataclass(text=text, code=message.code))

class SubmissionResultDataclass(RegistryDataclass):
    submitted_structure: SubmittedStructureDataclass = field()
    status_message: StatusMessageDataclass = field()

    class Meta:
        app = 'registry'
        model_name = 'SubmittedStructure'
        namespace_key = 'registry'

    def process_premake(self):
        return self._meta.model.objects.create(
            structure_submission=self._wrapper._obj,
            action = self._context.result.submitted_structure.action,
            external_dependencies = self._context.result.submitted_structure.external_dependencies,
            maintainable_object=self._context.maintainable
        )

    def process_postmake(self, obj):
        obj.status_message = self.m_status_message
        obj.save()
        return obj

class SubmitStructureResponseDataclass(RegistryDataclass):
    submission_result: Iterable[SubmissionResultDataclass] = field()

class NotificationURLDataclass(RegistryDataclass):
    is_soap: str = field(localname='isSOAP', is_attribute=True)
    notification_url: str = field(is_text=True)

class ValidityPeriodDataclass(RegistryDataclass):
    start_date: date = field()
    end_date: date = field()

class IdentifiableObjectEventDataclass(RegistryDataclass):
    all_instances: EmptyDataclass = field(localname='All', default=False)
    urn: str = field(localname='URN')
    object_id: str = field(localname='ID', default='%')

class VersionableObjectEventDataclass(IdentifiableObjectEventDataclass):
    version: str = field(default='%')

class StructuralRepositoryEventsDataclass(RegistryDataclass):
    agency_id: Iterable[StringDataclass] = field(namespace_key='registry', localname='AgencyID', default='%')
    all_events: EmptyDataclass = field(namespace_key='registry', default=False)
    agency_scheme: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    data_consumer_scheme: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    data_provider_scheme: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    organisation_unit_scheme: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    dataflow: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    metadataflow: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    category_scheme: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    categorisation: Iterable[IdentifiableObjectEventDataclass] = field(namespace_key='registry')
    codelist: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    hierarchical_codelist: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    concept_scheme: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    metadata_structure_definition: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    key_family: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    structure_set: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    reporting_taxonomy: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    process: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    attachment_constraint: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    content_constraint: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    provision_agreement: Iterable[VersionableObjectEventDataclass] = field(namespace_key='registry')
    event_type: str = field(is_attribute=True, localname='TYPE', default='STRUCTURE')

class EventSelectorDataclass(RegistryDataclass):
    structural_repository_events: StructuralRepositoryEventsDataclass = field()
    # data_registration_events: DataRegistrationEvents = field(namespace_key='registry')
    # metadata_registration_events: MetadataRegistrationEvents = field(namespace_key='registry')

class SubscriptionDataclass(RegistryDataclass):
    organisation: ReferenceDataclass = field()
    registry_urn: str = field(localname='RegistryURN')
    notification_mail_to: Iterable[NotificationURLDataclass] = field()
    notification_http: Iterable[NotificationURLDataclass] = field(localname='NotificationHTTP')
    subscriber_assigned_id: str = field(localname='SubscriberAssignedID')
    validity_period: ValidityPeriodDataclass = field()
    event_selector: EventSelectorDataclass = field() 
    action: str = field(is_attribute=True)

class SubmitSubscriptionsRequestDataclass(RegistryDataclass):
    subscription_request: Iterable[SubscriptionDataclass] = field()

class SubscriptionStatusDataclass(RegistryDataclass):
    subscription_urn: str = field(localname='SubscriptionURN')
    subscriber_assigned_id: str = field(localname='SubscriberAssignedID')
    status_message: StatusMessageDataclass = field()

class SubmitSubscriptionsResponseDataclass(RegistryDataclass):
    subscription_status: Iterable[SubscriptionStatusDataclass] = field()

class QuerySubscriptionRequestDataclass(RegistryDataclass):
    organisation: ReferenceDataclass = field()

class QuerySubscriptionResponseDataclass(RegistryDataclass):
    status_message: StatusMessageDataclass = field()
    subscription: Iterable[SubscriptionDataclass] = field()

class StructuralEventDataclass(RegistryDataclass):
    structures: StructuresDataclass = field(namespace_key='structure')

# # class RegistrationEvent(RegistryDataclass):
#     registration: Registration = field(namespace_key='registry')

class NotifyRegistryEventDataclass(RegistryDataclass):
    event_time: datetime = field()
    object_urn: str = field(localname='ObjectURN')
    registration_id: str = field(localname='RegistrationID')
    subscription_urn: str = field(localname='SubscriptionURN')
    event_action: str = field()
    structural_event: StructuralEventDataclass = field()
    # registration_event: RegistrationEvent = field()

class RegistryInterfaceSubmitStructureRequestDataclass(BaseSDMXMessageDataclass):
    submit_structure_request: SubmitStructureRequestDataclass = field()

    def to_response(self):
        data = RegistryInterfaceSubmitStructureResponseDataclass(
            header=self.header.to_response(),
            submit_structure_response=self.submit_structure_request.to_response()
        )
        return data

class RegistryInterfaceSubmitStructureResponseDataclass(BaseSDMXMessageDataclass):
    submit_structure_response: SubmitStructureResponseDataclass = field()

class RegistryInterface(BaseSDMXMessageDataclass):

    # submit_registrations_request: SubmitRegistrationsRequestDataclass = field() 
    # submit_registrations_response: SubmitRegistrationsResponseDataclass = field()
    # query_registration_request: QueryRegistrationRequestDataclass = field()
    # query_registration_response: QueryRegistrationResponseDataclass = field()
    submit_structure_request: SubmitStructureRequestDataclass = field()
    submit_structure_response: SubmitStructureResponseDataclass = field()
    submit_subscriptions_request: SubmitSubscriptionsRequestDataclass = field()
    submit_subscriptions_response: SubmitSubscriptionsResponseDataclass = field()
    query_subscription_request: QuerySubscriptionRequestDataclass = field()
    query_subscription_response: QuerySubscriptionResponseDataclass = field()
    notify_registry_event: NotifyRegistryEventDataclass = field()
