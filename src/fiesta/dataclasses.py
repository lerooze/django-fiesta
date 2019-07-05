from django.db.models import Q
from functools import reduce
from fiesta.core import status
from fiesta.core import constants
from fiesta.parsers import XMLParser
from fiesta.core.dataclasses import FiestaDataclass, field, Empty
from fiesta.core import patterns
from dataclasses import asdict
from collections import defaultdict
from typing import Iterable
from inflection import underscore
from datetime import datetime, date, timedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from fiesta.utils.translation import get_language
from django.utils import translation
from fiesta.settings import api_settings
from django.apps import apps
from django.db import transaction
from decimal import Decimal
from django.core.files.base import ContentFile
from rest_framework.exceptions import ParseError 

class CommonDataclass(FiestaDataclass):

    class Meta:
        app = 'common'

class BaseDataclass(FiestaDataclass):

    class Meta:
        app = 'base'

class RegistryDataclass(FiestaDataclass):

    app = 'registry'

class TextDataclass(SimpleStringDataclass):

    lang: str = field(is_attribute=True, namespace_key='xml', default='en')

    class Meta:
        app = 'common' 
        model_name = 'Text'

    def preprocess_isvalid(self):
        if not self.lang in settings.LANGUAGES: 
            self._context.result.status_message.update(
                'Failure',
                status.FIESTA_2501_NOT_SUPPORTED_LANGUAGE
            )

    def preprocess_make_obj(self):
        return self._meta.model.get_or_create(
            polymorphic_obj=self._wrapper._obj,
            text=self.text,
            text_type=self._field_name,
            language=self.lang
        )

    @classmethod
    def generate_many(cls, related_obj, specifier, *args, **kwargs):
        for obj in cls._meta.model.get_polymorphic(related_obj, specifier):
            for lang in settings.LANGUAGES:
                yield cls(
                    text=getattr(obj, f'text_{lang}', None),
                    lang=LangDataclass(lang=lang)
                )

class NameDataclass(TextDataclass):
    pass

class DescriptionDataclass(TextDataclass):
    pass

class DepartmentDataclass(TextDataclass):
    pass

class RoleDataclass(TextDataclass):
    pass

class RefDataclass(CommonDataclass):
    agency_id: str = field(is_attribute=True, localname='agencyID')
    maintainable_parent_id: str = field(is_attribute=True, localname='maintainableParentID')
    maintainable_parent_version: str = field(is_attribute=True)
    container_id: str = field(is_attribute=True, localname='containerID')
    object_id: str = field(is_attribute=True, localname='id')
    version: str = field(is_attribute=True)
    local: bool = field(is_attribute=True)
    cls: str= field(is_attribute=True, localname='class')
    package: str = field(is_attribute=True)

class ReferenceDataclass(CommonDataclass):
    ref: RefDataclass = field()
    urn: SimpleStringDataclass = field(localname='URN')

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.dref = self._urn_to_ref(self.urn) or self.ref

    def make_maintainable_urn(self):
        if self.urn: return self.urn
        d = self.dref
        urn = f'urn:sdmx:infomodel.{d.package}.{d.cls}={d.agency}:{d.object_id}({d.version})' 
        return urn

    def _urn_to_ref(self, urn):
        if not urn: return
        ref = RefDataclass()
        lurn, rurn = urn.split('=')
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

class BaseContactDataclass(FiestaDataclass):

    name: Iterable[TextDataclass] = field(namespace_key='common')
    department: Iterable[TextDataclass] = field(namespace_key='message')
    role: Iterable[TextDataclass] = field(namespace_key='message')
    telephone: Iterable[SimpleStringDataclass] = field(namespace_key='message')
    fax: Iterable[SimpleStringDataclass] = field(namespace_key='message', related_name='faxes')
    x400: Iterable[SimpleStringDataclass] = field(namespace_key='message')
    uri: Iterable[SimpleStringDataclass] = field(namespace_key='message', localname='URI')
    email: Iterable[SimpleStringDataclass] = field(namespace_key='message')

    class Meta:
        app = 'base'
        model_name = 'Contact'

class ContactDataclass(BaseContactDataclass):

    def preprocess_isvalid(self):
        if not self.email:
            self._context.result.status_message.update(
                'Warning', 
                status.FIESTA_2404_NO_EMAIL
            )
            self._stop= True

    def preprocess_make_obj(self):
        username = list(self.email)[0]
        obj, self._new_user = self._meta.model.objects.get_or_create(
            username, self.telephone, self.fax, self.x400, self.uri)
        return obj

    def postprocess_make_obj(self, obj):
        if self._new_user:
            obj.send_password_reset_email(self._context.request)
        obj.save()
        return obj

class HeaderContactDataclass(BaseContactDataclass):

    def preprocess_isvalid(self):
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

    def preprocess_make_obj(self):
        self._inner_stop = True
        return self._obj

class PartyDataclass(FiestaDataclass):

    name: Iterable[TextDataclass] = field(namespace_key='common')
    contact: Iterable[HeaderContactDataclass] = field(namespace_key='message')
    object_id: str = field(is_attribute=True, localname='id')

    class Meta:
        app = 'base'
        model_name = 'Organisation'

    def preprocess_isvalid(self):
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

    def preprocess_make_obj(self):
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
    timezone: SimpleStringDataclass = field(namespace_key='message')

    def wsrest_sender(self):
        self.object_id = api_settings.DEFAULT_SENDER_ID 

class PayloadStructureDataclass(FiestaDataclass):
    provision_agreement: ReferenceDataclass = field(namespace_key='common')
    structure_usage: ReferenceDataclass = field(namespace_key='common')
    structure: ReferenceDataclass = field(namespace_key='common')
    structure_id: str = field(is_attribute=True, localname='structureID')
    schema_url: str = field(is_attribute=True, localname='schemaURL')
    namespace: str = field(is_attribute=True)
    dimension_at_observation: str = field(is_attribute=True)
    explicit_measures: str = field(is_attribute=True)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)


class HeaderDataclass(FiestaDataclass):
    object_id: SimpleStringDataclass = field(namespace_key='message', localname='ID')
    test: SimpleBooleanDataclass = field(namespace_key='message', default=False)
    prepared: SimpleDatetimeDataclass = field(namespace_key='message')
    sender: SenderDataclass = field(namespace_key='message')
    receiver: PartyDataclass = field(namespace_key='message')
    name: Iterable[TextDataclass] = field(namespace_key='common')
    structure: Iterable[PayloadStructureDataclass] = field(namespace_key='message')
    data_provider: ReferenceDataclass = field(namespace_key='message')
    data_set_action: SimpleStringDataclass = field(namespace_key='message')
    data_set_id: SimpleStringDataclass = field(namespace_key='message', localname='DataSetID')
    extracted: SimpleDatetimeDataclass = field(namespace_key='message')
    reporting_begin: SimpleStringDataclass = field(namespace_key='message')
    reporting_end: SimpleStringDataclass = field(namespace_key='message')
    embargo_date: SimpleDatetimeDataclass = field(namespace_key='message')
    source: SimpleStringDataclass = field(namespace_key='message')

    class Meta:
        app = 'registry'
        model_name = 'Submission'

    def to_reference(self):
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
        reference = self.to_reference()
        submitted_structure = SubmittedStructureDataclass(
            maintainable_object=reference, 
        )
        submission_result = submitted_structure.to_result()
        return submission_result

    def preprocess_isvalid(self):
        self._context.acquisition.progress = 'Processing'
        self._context.acquisition.save()
        self._context['result'] = self.get_or_add_result(self.to_submission_result())

    def postprocess_make_obj(self, obj):
        super().postprocess_make_obj(obj)
        obj = self._meta.model.objects.create(
            acquisition=self._context.acquisition,
            object_id=self.object_id,
            test=self.test,
            prepared=self.prepared,
            sender=self.m_sender,
            receiver=self.m_receiver,
        )
        obj.sender_contacts.add(*self.sender.m_contact)
        obj.receiver_contacts.add(*self.receiver.m_contact)
        acquisition_file = ContentFile(self._context.request.stream)
        self._context.acquisition_obj.acquisition_file.save(f'Ref_{obj.id}.xml',
                                                            acquisition_file)
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

    def to_structure(self, registration):
        self.object_id=registration.id,
        self.test=False,
        self.prepared=registration.prepared,
        self.sender=SenderDataclass().wsrest_sender(),
        self.receiver=PartyDataclass().wsrest_party(registration),

class AnnotationTextDataclass(TextDataclass):
    pass

class AnnotationDataclass(CommonDataclass):
    annotation_title: SimpleStringDataclass = field(namespace_key='common')
    annotation_type: SimpleStringDataclass = field(namespace_key='common')
    annotation_url: SimpleStringDataclass = field(namespace_key='common', localname='AnnotationURL')
    annotation_text: Iterable[TextDataclass] = field(namespace_key='common')
    object_id: str = field(is_attribute=True, localname='id')

    class Meta:
        app = 'common'
        model_name = 'Annotation'

    def preprocess_make_obj(self):
        obj, _ = self._meta.model.objects.get_or_create(
            object_id=self.object_id,
            annotation_title=self.annotation_title,
            annotation_type=self.annotation_type,
            annotation_url=self.annotation_url,
            annotable_object=self._wrapper._obj,
        )
        return obj

    @classmethod
    def generate(cls, related_obj, *args, **kwargs):
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

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not obj.object_id:
            obj.object_id = self.object_id
        return obj

class NameableDataclass(IdentifiableDataclass):
    name: Iterable[NameDataclass] = field(namespace_key='common')
    description: Iterable[DescriptionDataclass] = field(namespace_key='common')

class VersionableDataclass(NameableDataclass):
    version: str = field(is_attribute=True, default='1.0')
    valid_from: datetime = field(is_attribute=True)
    valid_to: datetime = field(is_attribute=True)

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not obj.version:
            obj.version = self.version
        if not obj.valid_from:
            obj.valid_from = self.valid_from
        if not obj.valid_to:
            obj.valid_to = self.valid_to
        return obj

class MaintainableDataclass(VersionableDataclass):
    agency_id: str = field(is_attribute=True, localname='agencyID', forward=True)
    is_final: bool = field(is_attribute=True, default=False)
    is_external_reference: bool = field(is_attribute=True, default=False)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)

    def make_structure_url(self):
        resource = constants.CLASS2RESOURCE(self._meta.name)[0]
        return f'http://www.fiesta.org/{resource}/{self.agency_id}/{self.version}'

    @classmethod
    def generate(cls, queries_kwargs):
        kwargs = queries_kwargs[cls]
        if not kwargs: return
        kwargs = reduce(lambda x, y: x | y, [Q(**item) for item in kwargs])
        for obj in cls._meta.model.objects.filter(kwargs):
            yield obj

    @classmethod
    def build_main_query(cls, registration):
        kwargs = {}
        if registration.resource_id != 'all':
            kwargs['object_id'] = registration.resource_id
        if registration.agency_id != 'all':
            kwargs['agency__object_id'] = registration.agency_id
        if registration.version == 'latest':
            kwargs['latest'] = True
        elif registration.version != 'all':
            kwargs['version'] = registration.version
        return kwargs 

    @classmethod
    def build_other_queries(cls, sibling_cls, base_Q):
        return {}

    @classmethod
    def queries_append(cls, registration, queries, depth):
        refs = registration.references
        base_query = queries[cls]
        if not depth:
            base_query.append(cls.build_main_query(registration))
        depth += 1
        if refs in ['children', 'parentsandsiblings'] and depth == 1:
            for child_cls in cls._meta.children.values():
                base_Q = reduce(lambda x, y: x | y, [Q(**item) for item in base_query])
                other_query = child_cls.build_other_queries(cls, base_Q)
                queries[child_cls].append(other_query)
        elif registration.references in ['descendants', 'all'] and depth >= 1:
            for child_cls in cls._meta.children.values():
                base_Q = reduce(lambda x, y: x | y, [Q(**item) for item in base_query])
                other_query = child_cls.build_other_queries(cls, base_Q)
                queries[child_cls].append(other_query)
            for child_cls in cls._meta.children.values():
                child_cls.queries_append(registration, queries, depth)
        else:
            child_cls = cls._meta.children[refs]
            other_query = child_cls.build_other_queries(cls, base_Q)
            queries[child_cls].append(other_query)
        if refs in ['parents', 'parentsandsiblings', 'all'] and depth == 1:
            for parent_cls in cls._meta.parents.values():
                other_query = parent_cls.build_other_queries(cls, base_Q)
                queries[parent_cls].append(other_query)


    # @staticmethod
    # def modify_querysets(registration):
    #     kwargs = super().build_filter_kwargs(registration)
    #     if registration.resource == 'agencyscheme':  
    #         kwargs['object_id'] = 'AGENCIES'
    #     elif registration.resource == 'dataconsumerscheme':  
    #         kwargs['object_id'] = 'DATA_CONSUMERS'
    #     elif registration.resource == 'dataproviderscheme':  
    #         kwargs['object_id'] = 'DATA_PROVIDERS'
    #     else:
    #         if registration.resource_id != 'all':
    #             kwargs['object_id'] = registration.resource_id 
    #     return kwargs

    def get_external(self):
        location = self.structure_url
        status_message = self._result.status_message
        if not location:
            status_message.update(
                'Failure',
                status.FIESTA_2103_SOAP_PULLING_NOT_IMPLEMENTED
            ) 
            return
        message = XMLParser().get(location)
        if not isinstance(message, StructureDataclass):
            status_message.update(
                'Failure', 
                status.FIESTA_2201_PULLED_NOT_STRUCTURE
            ) 
            return
        structures = asdict(message.structures)
        wrapper = underscore(self._meta.class_wrapper)
        structure = underscore(self._meta.class_name)
        try:
            obj = list(structures[wrapper][structure])[0]
        except (IndexError, KeyError, AttributeError):
            status_message.update(
                'Failure', 
                status.FIESTA_2202_PULLED_NO_CONTENT_STRUCTURE) 
            return

        obj_stub = (obj.agency_id, obj.object_id, obj.version) 
        self_stub = (self.agency_id, self.object_id, self.version)
        if obj_stub != self_stub:
            status_message.update(
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

    def preprocess_isvalid(self):
        self._context['result'] = self.get_or_add_result(self.to_submission_result())
        model = apps.get_model('base', 'Organisation')
        try:
            self.agency = model.objects.get(object_id=self.agency_id)
        except model.DoesNotExist:
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2403_AGENCY_NOT_REGISTERED,
            )
            self._inner_stop = True

    def reset_latest(self, created):
        if not created: return
        objects = self._meta.model.filter(object_id=self.object_id,
                                          agency__object_id=self.agency_id)
        objects = objects.exclude(version=self.version)
        for obj in objects:
            obj.latest = False
            obj.save()

    def preprocess_make_obj(self):
        if self.is_external_reference:
            sdmxobj = self.get_external()
            self = sdmxobj
        obj, created = self._meta.model.objects.get_or_create(
            agency=self.agency,
            object_id=self.object_id,
            version=self.version
        )
        self.reset_latest(created)
        return obj 

    def preprocess_isobjvalid(self, obj):
        action = self._submission.submitted_structure.action
        if action in ['Replace', 'Delete']:
            if obj.is_final:
                self._context.result.status_message.update(
                    'Failure',
                    status.FIESTA_2101_MODIFICATION_NOT_ALLOWED
                ) 
            else:
                obj.delete()
                if action == 'Delete':
                    self._context.result.status_message.update(
                        'Success',
                    ) 

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not obj.is_final:
            obj.is_final = self.is_final
        self._context.result.status_message.update('Success')
        self._context.maintainable_obj = obj
        self._context.result.process(context=self._context)
        return obj

class ItemSchemeDataclass(MaintainableDataclass):
    is_partial: bool = field(is_attribute=True, default=False)

class StructuresItemsDataclass(BaseDataclass):

    def queries_append(self, registration, queries):
        for key, value in self._meta.fields:
            maintainable_type = value.type.__args__[0]
            maintainable_type.queries_append(registration, queries, depth=0)

class BaseItemDataclass(NameableDataclass):
    parent: ReferenceDataclass = field(namespace_key='common')

    def parse_obj(self):
        super().parse_obj()
        self.parent = self.create_parent_reference(self._obj)

    @classmethod
    def create_parent_reference(cls, obj):
        parent = obj.get_parent()
        if parent:
            return ReferenceDataclass(
                ref=RefDataclass(object_id=parent.object_id)
            )

class ItemDataclass(BaseItemDataclass):

    @classmethod
    def generate(cls, related_obj, specifier, *args, **kwargs):
        for obj in getattr(related_obj, specifier):
            yield cls(obj=item_obj)

    def get_parent(self, parent_id):
        return self._meta.model.objects.get(object_id=parent_id,
                                            wrapper=self._wrapper._obj)

    def preprocess_isvalid(self):
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

    def preprocess_make_obj(self):
        return self._meta.model.get_or_create(
            object_id=self.object_id,
            wrapper=self._wrapper._obj,
            parent=self._parent_obj
        )

class ManyToManyItemDataclass(ItemDataclass):

    def get_parent(self, parent_id):
        return self._meta.model.objects.get(object_id=parent_id)

    def preprocess_isvalid(self):
        super().preprocess_isvalid()
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
        model_name = 'Organisation'

class Agency(OrganisationDataclass):
    pass

class DataProvider(OrganisationDataclass):
    pass

class DataConsumer(OrganisationDataclass):
    pass

class OrganisationUnit(OrganisationDataclass):
    pass

class OrganisationSchemeDataclass(ItemSchemeDataclass):

    class Meta:
        app = 'base'
        model_name = 'OrganisationScheme'

class AgencySchemeDataclass(OrganisationSchemeDataclass):
    agency: Iterable[Agency] = field(namespace_key='structure', related_name='organisations') 

    @classmethod
    def build_main_query(cls, registration):
        if registration.resource != ['organisationscheme', 'agencyscheme']:
            return {}
        kwargs = super().build_main_query(registration)
        resource_id = kwargs.get('object_id')
        if registration.resource == 'agencyscheme' and resource_id and resource_id != 'AGENCIES':
            raise ParseError('The resourceID of an agencyscheme query must be equal to AGENCIES if set')
        kwargs.setdefault('object_id', 'AGENCIES')
        return kwargs

class DataConsumerSchemeDataclass(OrganisationSchemeDataclass):
    data_consumer: Iterable[DataConsumer] = field(namespace_key='structure', related_name='organisations') 

    @classmethod
    def build_main_query(cls, registration):
        if registration.resource != ['organisationscheme', 'dataconsumerscheme']:
            return {}
        kwargs = super().build_main_query(registration)
        resource_id = kwargs.get('object_id')
        if registration.resource == 'dataconsumerscheme' and resource_id and resource_id != 'DATA_CONSUMERS':
            raise ParseError('The resourceID of a dataconsumerscheme query must be equal to DATA_CONSUMERS if set')
        kwargs.setdefault('object_id', 'DATA_CONSUMERS')
        return kwargs

class DataProviderSchemeDataclass(OrganisationSchemeDataclass):
    data_provider: Iterable[DataProvider] = field(namespace_key='structure', related_name='organisations') 

    @classmethod
    def build_main_query(cls, registration):
        if registration.resource != ['organisationscheme', 'dataproviderscheme']:
            return {}
        kwargs = super().build_main_query(registration)
        resource_id = kwargs.get('object_id')
        if registration.resource == 'dataproviderscheme' and resource_id and resource_id != 'DATA_PROVIDERS':
            raise ParseError('The resourceID of a dataproviderscheme query must be equal to DATA_PROVIDERS if set')
        kwargs.setdefault('object_id', 'DATA_PROVIDERS')
        return kwargs

class OrganisationUnitSchemeDataclass(OrganisationSchemeDataclass):
    organisation_unit: Iterable[OrganisationUnit] = field(namespace_key='structure', related_name='organisations') 
    def build_main_query(cls, registration):
        if registration.resource != ['organisationscheme', 'organisationunitscheme']:
            return {}
        return super().build_main_query(registration)


class OrganisationSchemesDataclass(StructuresItemsDataclass):
    agency_scheme: Iterable[AgencySchemeDataclass] = field(namespace_key='structure')
    data_consumer_scheme: Iterable[DataConsumerSchemeDataclass] = field(namespace_key='structure')
    data_provider_scheme: Iterable[DataProviderSchemeDataclass] = field(namespace_key='structure')
    organisation_unit_scheme: Iterable[OrganisationUnitSchemeDataclass] = field(namespace_key='structure')

    class Meta:
        app = 'base'

class CodeDataclass(ItemDataclass):
    class Meta:
        app = 'codelist'

class CodelistDataclass(ItemSchemeDataclass):
    code: Iterable[CodeDataclass] = field(namespace_key='structure') 

    class Meta:
        app = 'codelist'

    @classmethod
    def build_other_queries(cls, sibling_cls, base_Q):
        kwargs = super().build_other_queries(sibling_cls, base_Q)
        if sibling_cls == ConceptSchemeDataclass:
            kwargs['enumerations__concepts__wrapper__in'] = sibling_cls.objects.filter(base_Q)
        return kwargs

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

    def preprocess_make_obj(self):
        obj, _ = self._meta.model.objects.get_or_create(
            **asdict(self)
        )
        return obj

class RepresentationDataclass(FiestaDataclass):
    text_format: FormatDataclass = field(namespace_key='common')
    enumeration: ReferenceDataclass = field(namespace_key='common')
    enumeration_format: FormatDataclass = field(namespace_key='common')

    class Meta:
        app = 'common' 

    def parse_obj(self):
        super().parse_dbobj()
        if self.enumeration:
            self.enumeration.cls = 'Codelist'
            self.enueration.package = 'codelist'
            
    def preprocess_make_obj(self):
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
    concept_agency: SimpleStringDataclass = field(namespace_key='structure')
    concept_scheme_id: SimpleStringDataclass = field(namespace_key='structure', localname='ConceptSchemeID')
    concept_id: SimpleStringDataclass = field(namespace_key='structure', localname='ConceptID')

    class Meta:
        app = 'conceptscheme'

    def preprocess_make_obj(self):
        obj, _ = self._meta.model.objects.get_or_create(
            asdict(self))
        return obj

class ConceptDataclass(ItemDataclass):
    core_representation: RepresentationDataclass = field(namespace_key='structure')
    iso_concept_reference: ISOConceptReferenceDataclass = field(
        namespace_key='structure', localname='ISOConceptReference')

    class Meta:
        app = 'conceptscheme'

    def postprocess_make_obj(self, obj):
        super().postprocess_make_obj(obj)
        if not obj.core_representation:
            obj.core_representation = self.m_core_representation
        if not obj.iso_concept_reference:
            obj.iso_concept_reference = self.m_iso_concept_reference
        obj.save()
        return obj

class ConceptSchemeDataclass(ItemSchemeDataclass):
    concept: Iterable[ConceptDataclass] = field() 

    class Meta:
        app = 'conceptscheme'
        children = [CodelistDataclass]

class ConceptsDataclass(StructuresItemsDataclass):
    concept_scheme: Iterable[ConceptSchemeDataclass] = field(namespace_key='structure')

class StructuresDataclass(FiestaDataclass):
    organisation_schemes: OrganisationSchemesDataclass = field(namespace_key='structure')
    # dataflows: DataflowsDataclass = field(namespace_key='registry')
    # metadataflows: MetadataflowsDataclass = field(namespace_key='registry')
    # category_schemes: CategorySchemesDataclass = field(namespace_key='registry')
    # categorisations: CategorisationsDataclass = field(namespace_key='registry')
    codelists: CodelistsDataclass = field(namespace_key='structure')
    # hierarchical_codelists: HierarchicalCodelistsDataclass = field(namespace_key='registry')
    concepts: ConceptsDataclass = field(namespace_key='structure')
    # metadata_structures: MetadataStructuresDataclass = field(namespace_key='registry')
    # data_structures: DataStructuresDataclass = field(namespace_key='registry')
    # structure_sets: StructureSetsDataclass = field(namespace_key='registry')
    # reporting_taxonomies: ReportingTaxonomiesDataclass = field(namespace_key='registry')
    # processes: ProcessesDataclass = field(namespace_key='registry')
    # constraints: ConstraintsDataclass = field(namespace_key='registry')
    # provision_agreements: ProvisionAgreementsDataclass = field(namespace_key='registry')

    def retrieve(self, registration):
        queries = defaultdict(list)
        structures = underscore(constants.RESOURCE2STRUCTURE[registration.resource])
        if type(structures) != list: structures = [structures]
        for structure in structures:
            structure_type = self._meta.fields[structure].type
            structure_type.queries_append(registration, queries)
        for key, value in queries.items():
            wrapper = underscore(constants.CLASS2WRAPPER(key.__name__))
            wrapper_model = self._meta.fields[wrapper].type
            wrapper_field = getattr(self, wrapper)
            if not wrapper_field:
                setattr(self, wrapper, wrapper_model())
            wrapper_field = getattr(self, wrapper)
            setattr(wrapper_field, underscore(key.__name__),
                    value.generate(queries))

class MessageDataclass(FiestaDataclass):

    text: Iterable[TextDataclass] = field(namespace_key='common')
    code: str = field(is_attribute=True)
    severity: str = field(is_attribute=True)

class FooterDataclass(FiestaDataclass):
    message: Iterable[MessageDataclass] = field()

    class Meta:
        namespace_key = 'footer'

    def preprocess_isvalid(self):
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

class StructureDataclass(FiestaDataclass):
    header: HeaderDataclass = field(namespace_key='message')
    structures: StructuresDataclass = field(namespace_key='message')
    footer: FooterDataclass = field(namespace_key='footer')

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

    def retrieve(self, registration):
        self.structures = StructuresDataclass().retrieve(registration)
        registration.save()
        self.header = HeaderDataclass().to_structure(registration)

class SubmittedStructureDataclass(RegistryDataclass):
    maintainable_object: ReferenceDataclass = field(namespace_key='registry')
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True)

    def to_result(self):
        new_self = self.__class__(
            maintainable_object=self.maintainable_object,
            action=self.action or self._wrapper.action,
            external_dependencies=self.external_dependencies or self._wrapper.external_dependencies
        )
        return SubmissionResultDataclass(
            submitted_structure=new_self,
            status_message=StatusMessageDataclass()
        )

class SubmitStructureRequestDataclass(RegistryDataclass):
    structure_location: SimpleStringDataclass = field(namespace_key='registry') 
    structures: StructuresDataclass = field(namespace_key='structure')
    submitted_structure: Iterable[SubmittedStructureDataclass] = field(namespace_key='registry')
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True) 

    class Meta:
        app = 'registry'
        model = 'SubmitStructure'

    def preprocess_isvalid(self):
        if not self.structures:
            loc = self.structure_location
            message = XMLParser().get(loc)
            if not isinstance(message, StructureDataclass):
                self._wrapper._obj.delete()
                self._context.result.status_message.update(
                    'Failure',
                    status.FIESTA_2201_PULLED_NOT_STRUCTURE
                )
            self.structures = message.structures
        if self._context.result.status_message.status == 'Failure':
            self._stop = True 

    def preprocess_make_obj(self):
        obj = self._meta.model.objects.create(
            submission=self._wrapper.m_header,
            structure_location=self.structure_location,
            action=self.action,
            external_dependencies=self.external_dependencies
        )
        for submitted_structure in self.submitted_structure:
            submission_result = submitted_structure.to_result()
            submission_result._wrapper = obj
            self.get_or_add_result(submitted_structure.to_result())
        return obj

    def postprocess_isvalid(self):
        self._wrapper.m_header.save()

    def to_response(self):
        return SubmitStructureResponseDataclass(
            submission_result = self.submission_results() 
        )

    def submission_results(self):
        for package, vp in self._context.submitted_structure_results.items():
            for cls, vc in vp.items():
                for agency, va in vc.items():
                    for object_id, vo in va.items():
                        for version, result in vo.items():
                            yield result 

class StatusMessageTextDataclass(RegistryDataclass):
    text: Iterable[TextDataclass] = field(namespace_key='common')
    code: str = field(is_attribute=True)

    def preprocess_make_obj(self):
        obj, _ = self._meta.model.objects.get_or_create(
            code = self.code 
        )
        return obj

class StatusMessageDataclass(RegistryDataclass):
    message_text: Iterable[StatusMessageTextDataclass] = field(namespace_key='registry')
    status: str = field(is_attribute=True)

    def preprocess_make_obj(self):
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
    submitted_structure: SubmittedStructureDataclass = field(namespace_key='registry')
    status_message: StatusMessageDataclass = field(namespace_key='registry')

    class Meta:
        app = 'registry'
        model_name = 'SubmittedStructure'

    def preprocess_make_obj(self):
        return self._meta.model.objects.create(
            structure_submission=self._wrapper._obj,
            action = self._context.result.submitted_structure.action,
            external_dependencies = self._context.result.submitted_structure.external_dependencies,
            maintainable_object=self._context.maintainable_obj
        )

    def postprocess_make_obj(self, obj):
        obj.status_message = self.m_status_message
        obj.save()
        return obj

class SubmitStructureResponseDataclass(RegistryDataclass):
    submission_result: Iterable[SubmissionResultDataclass] = field(namespace_key='registry')

class NotificationURLDataclass(RegistryDataclass):
    is_soap: str = field(localname='isSOAP', is_attribute=True)
    notification_url: str = field(is_text=True)

class ValidityPeriodDataclass(RegistryDataclass):
    start_date: SimpleDateDataclass = field(namespace_key='registry')
    end_date: SimpleDateDataclass = field(namespace_key='registry')

class IdentifiableObjectEventDataclass(RegistryDataclass):
    all_instances: EmptyDataclass = field(namespace_key='registry', localname='All', default=False)
    urn: SimpleStringDataclass = field(namespace_key='registry', localname='URN')
    object_id: SimpleStringDataclass = field(namespace_key='registry', localname='ID', default='%')

class VersionableObjectEventDataclass(IdentifiableObjectEventDataclass):
    version: SimpleStringDataclass = field(namespace_key='registry', default='%')

class StructuralRepositoryEventsDataclass(RegistryDataclass):
    agency_id: Iterable[SimpleStringDataclass] = field(namespace_key='registry', localname='AgencyID', default='%')
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
    structural_repository_events: StructuralRepositoryEventsDataclass = field(namespace_key='registry')
    # data_registration_events: DataRegistrationEvents = field(namespace_key='registry')
    # metadata_registration_events: MetadataRegistrationEvents = field(namespace_key='registry')

class SubscriptionDataclass(RegistryDataclass):
    organisation: ReferenceDataclass = field(namespace_key='registry')
    registry_urn: SimpleStringDataclass = field(namespace_key='registry', localname='RegistryURN')
    notification_mail_to: Iterable[NotificationURLDataclass] = field(namespace_key='registry')
    notification_http: Iterable[NotificationURLDataclass] = field(localname='NotificationHTTP')
    subscriber_assigned_id: SimpleStringDataclass = field(namespace_key='registry', localname='SubscriberAssignedID')
    validity_period: ValidityPeriodDataclass = field(namespace_key='registry')
    event_selector: EventSelectorDataclass = field(namespace_key='registry') 
    action: str = field(is_attribute=True)

class SubmitSubscriptionsRequestDataclass(RegistryDataclass):
    subscription_request: Iterable[SubscriptionDataclass] = field(namespace_key='registry')

class SubscriptionStatusDataclass(RegistryDataclass):
    subscription_urn: SimpleStringDataclass = field(namespace_key='registry', localname='Subscription_URN')
    subscriber_assigned_id: SimpleStringDataclass = field(namespace_key='registry', localname='SubscriberAssignedID')
    status_message: StatusMessageDataclass = field(namespace_key='registry')

class SubmitSubscriptionsResponseDataclass(RegistryDataclass):
    subscription_status: Iterable[SubscriptionStatusDataclass] = field(namespace_key='registry')

class QuerySubscriptionRequestDataclass(RegistryDataclass):
    organisation: ReferenceDataclass = field(namespace_key='registry')

class QuerySubscriptionResponseDataclass(RegistryDataclass):
    status_message: StatusMessageDataclass = field(namespace_key='registry')
    subscription: Iterable[SubscriptionDataclass] = field(namespace_key='registry')

class StructuralEventDataclass(RegistryDataclass):
    structures: StructuresDataclass = field(namespace_key='structure')

# # class RegistrationEvent(RegistryDataclass):
#     registration: Registration = field(namespace_key='registry')

class NotifyRegistryEventDataclass(RegistryDataclass):
    event_time: SimpleDatetimeDataclass = field(namespace_key='registry')
    object_urn: SimpleStringDataclass = field(localname='ObjectURN', namespace_key='registry')
    registration_id: SimpleStringDataclass = field(localname='RegistrationID', namespace_key='registry')
    subscription_urn: SimpleStringDataclass = field(localname='SubscriptionURN', namespace_key='registry')
    event_action: SimpleStringDataclass = field(namespace_key='registry')
    structural_event: StructuralEventDataclass = field(namespace_key='registry')
    # registration_event: RegistrationEvent = field(namespace_key='registry')

class BaseRegistryInterface(FiestaDataclass):
    header: HeaderDataclass = field(namespace_key='message')
    footer: FooterDataclass = field(namespace_key='footer')

class RegistryInterfaceSubmitStructureRequestDataclass(BaseRegistryInterface):
    submit_structure_request: SubmitStructureRequestDataclass = field(namespace_key='registry')

    def to_response(self):
        data = RegistryInterfaceSubmitStructureResponseDataclass(
            header=self.header.to_response(),
            submit_structure_response=self.submit_structure_request.to_response()
        )
        return data

class RegistryInterfaceSubmitStructureResponseDataclass(BaseRegistryInterface):
    submit_structure_response: SubmitStructureResponseDataclass = field()

class RegistryInterface(BaseRegistryInterface):
    # submit_registrations_request: SubmitRegistrationsRequestDataclass = field(namespace_key='registry') 
    # submit_registrations_response: SubmitRegistrationsResponseDataclass = field(namespace_key='registry)
    # query_registration_request: QueryRegistrationRequestDataclass = field(namespace_key='registry')
    # query_registration_response: QueryRegistrationResponseDataclass = field(namespace_key='registry')
    submit_structure_request: SubmitStructureRequestDataclass = field(namespace_key='registry')
    submit_structure_response: SubmitStructureResponseDataclass = field(namespace_key='registry')
    submit_subscriptions_request: SubmitSubscriptionsRequestDataclass = field(namespace_key='registry')
    submit_subscriptions_response: SubmitSubscriptionsResponseDataclass = field(namespace_key='registry')
    query_subscription_request: QuerySubscriptionRequestDataclass = field(namespace_key='registry')
    query_subscription_response: QuerySubscriptionResponseDataclass = field(namespace_key='registry')
    notify_registry_event: NotifyRegistryEventDataclass = field(namespace_key='registry')
