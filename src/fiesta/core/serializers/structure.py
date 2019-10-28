# structure.py

import functools
import lxml 

from dataclasses import asdict
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import transaction, ProtectedError
from django.db.models import Q
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ExternalError
from importlib import import_module
from lxml.etree import QName
from typing import Iterable, List

from .. import status, constants, patterns
from ...utils.translation import get_language
from ...settings import api_settings
from ...external import Request as ExternalRequest

from .base import field, Serializer, EmptySerializer

class CommonSerializer(Serializer):

    class Meta:
        namespace_key = 'common'

class RegistrySerializer(Serializer):

    class Meta:
        namespace_key = 'registry'

class StringSerializer(Serializer):
    text: str = field(is_text=True)

    def __post_init__(self, *args, **kwargs):
        if isinstance(self._instance, str):
            self.text = self._instance
        else:
            self.text = self._instance.text

class ValueSerializer(Serializer):
    text: str = field(is_text=True)
    cascade_values: bool = field(is_attribute=True, default=False)

class TextSerializer(Serializer):
    text: str = field(is_text=True)
    lang: str = field(is_attribute=True, namespace_key='xml', default='en')

    @classmethod
    def generate_many(cls, instance, forward_accesor):
        for lang in settings.LANGUAGES:
            text = getattr(instance, f'{forward_accesor}_lang')
            yield cls(lang=lang, text=text)

class SimpleStringSerializer(Serializer):
    value: str = field(is_text=True)

class SimpleStringContactSerializer(SimpleStringSerializer):

    def process_premake(self):
        return self._meta.model.create(
            value=self.value,
            contact=self._container._obj
        )

class ContactSerializer(Serializer):

    name: Iterable[TextSerializer] = field(namespace_key='common')
    department: Iterable[TextSerializer] = field()
    role: Iterable[TextSerializer] = field()
    telephone: Iterable[StringSerializer] = field(is_text=True)
    fax: Iterable[StringSerializer] = field(is_text=True)
    x400: Iterable[StringSerializer] = field(is_text=True)
    uri: Iterable[StringSerializer] = field(localname='URI', is_text=True)
    email: Iterable[StringSerializer] = field(is_text=True)

    class Meta:
        namespace_key = 'message'

class MaintainableRefSerializer(Serializer):
    agency_id: str = field(localname='agencyID', is_attribute=True,
                           forward=True, forward_accesor='agency__object_id')
    object_id: str = field(localname='id', is_attribute=True)
    version: str = field(is_attribute=True)
    local: bool = field(is_attribute=True, default=False)
    cls: str= field(localname='class', is_attribute=True)
    package: str = field(is_attribute=True)

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if not self._instance: return
        object_name = self._instance.__class__._meta.object_name
        if object_name == 'codelistreference':
            self.cls = 'Codelist'
            self.package = 'codelist'
        elif object_name == 'conceptschemereference':
            self.cls = 'ConceptScheme'
            self.package = 'conceptscheme'
        elif object_name == 'datastructurereference':
            self.cls = 'DataStructure'
            self.package = 'datastructure'
        elif object_name == 'dataflowreference':
            self.cls = 'Dataflow'
            self.package = 'datastructure'
        elif object_name == 'attachmentconstraintreference':
            self.cls = 'AttachmentConstraint'
            self.package = 'registry'
        elif object_name == 'contentconstraintreference':
            self.cls = 'ContentConstraint'
            self.package = 'registry'
        elif object_name == 'provisionagreementreference':
            self.cls = 'ProvisionAgreement'
            self.package = 'registry'

class ItemRefSerializer(Serializer):
    agency_id: str = field(localname='agencyID', is_attribute=True,
                           forward=True, forward_accesor='agency__object_id')
    maintainable_parent_id: str = field(localname='maintainableParentID', is_attribute=True, forward=True, forward_accesor='object_id')
    maintainable_parent_version: str = field(is_attribute=True, forward=True, forward_accesor='version')
    object_id: str = field(localname='id', is_attribute=True, forward_accesor='item_object_id')
    version: str = field(is_attribute=True)
    local: bool = field(is_attribute=True, default=False)
    cls: str= field(localname='class', is_attribute=True)
    package: str = field(is_attribute=True)

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if not self._instance: return
        object_name = self._instance.__class__._meta.object_name
        if object_name == 'codereference':
            self.cls = 'Code'
            self.package = 'codelist'
        elif object_name == 'conceptreference':
            self.cls = 'Concept'
            self.package = 'conceptscheme'
        elif object_name == 'dataproviderreference':
            self.cls = 'DataProvider'
            self.package = 'base'
        elif object_name == 'dataconsumerreference':
            self.cls = 'DataConsumer'
            self.package = 'base'
        elif object_name == 'organisationunitreference':
            self.cls = 'OrganisationUnit'
            self.package = 'base'

class LocalRefSerializer(Serializer):
    object_id: str = field(localname='id', is_attribute=True, forward_accesor='object_id')
    local: bool = field(is_attribute=True, default=True)
    cls: str= field(localname='class', is_attribute=True)
    package: str = field(is_attribute=True)

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if not self._instance: return
        object_name = self._instance.__class__._meta.object_name
        if object_name == 'code':
            self.cls = 'Code'
            self.package = 'codelist'
        elif object_name == 'concept':
            self.cls = 'Concept'
            self.package = 'conceptscheme'
        elif object_name == 'organisationunit':
            self.cls = 'OrganisationUnit'
            self.package = 'base'
        elif object_name == 'Dimension':
            self.cls = 'Dimension'
            self.package = 'datastructure'
        elif object_name == 'Group':
            self.cls = 'Group'
            self.package = 'datastructure'
        elif object_name == 'primarymeasure':
            self.cls = 'PrimaryMeasure'
            self.package = 'datastructure'


class ReferenceSerializer(Serializer):

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if self._element: 
            self.dref = self._urn_to_ref() or self.ref

    def process_postmake(self):
        return self.m_ref

class MaintainableReferenceSerializer(ReferenceSerializer):
    ref: MaintainableRefSerializer = field(namespace_key='')
    urn: str = field(localname='URN', namespace_key='')

    def _urn_to_ref(self):
        if not self.urn: return
        ref = MaintainableRefSerializer()
        lurn, rurn = self.urn.split('=')
        lurn = lurn.split(':')[-1]
        _, ref.package, ref.cls = lurn.split('.')
        ref.agency_id, remaining = rurn.split(':')
        match = patterns.MAINTAINABLE.match(remaining)
        ref.object_id = match.group('object_id')
        ref.version = match.group('version') or '1.0'
        return ref

    def make_urn(self):
        if self.urn: return self.urn
        d = self.dref
        urn = f'urn:sdmx:infomodel.{d.package}.{d.cls}={d.agency_id}:{d.object_id}({d.version})' 
        return urn

class ItemReferenceSerializer(ReferenceSerializer):
    ref: ItemRefSerializer = field(namespace_key='')
    urn: str = field(localname='URN', namespace_key='')

    def _urn_to_ref(self):
        if not self.urn: return
        ref = ItemRefSerializer()
        lurn, rurn = self.urn.split('=')
        lurn = lurn.split(':')[-1]
        _, ref.package, ref.cls = lurn.split('.')
        ref.agency_id, remaining = rurn.split(':')
        match = patterns.PARENTABLE.match(remaining)
        ref.object_id = match.group('object_id')
        ref.version = match.group('version') or '1.0'
        ref.maintainable_parent_id = match.group('maintainable_parent_id')
        ref.maintainable_parent_version = match.group('maintainable_parent_version')
        ref.container_id = match.group('container_id')
        return ref

    def make_urn(self):
        if self.urn: return self.urn
        d = self.dref
        urn = f'urn:sdmx:infomodel.{d.package}.{d.cls}={d.agency_id}:{d.maintainable_parent_id}({d.maintainable_parent_version}).{d.object_id}' 
        return urn

class LocalReferenceSerializer(Serializer):
    ref: LocalRefSerializer = field(namespace_key='')


class AnnotationSerializer(Serializer):
    annotation_title: str = field(is_text=True)
    annotation_type: str = field(is_text=True)
    annotation_url: str = field(is_text=True, localname='AnnotationURL')
    annotation_text: Iterable[TextSerializer] = field(related_name='annotation_text')
    object_id: str = field(is_attribute=True, localname='id')

    class Meta:
        app_name = 'common'
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
    def generate_many(cls, instance, forward_accesor):
        annotation_set = instance.annotation_set
        return (cls(annotation) for annotation in annotation_set)


class AnnotationsSerializer(CommonSerializer):
    annotation: Iterable[AnnotationSerializer] = field(related_name='annotation_set')

class AnnotableSerializer(CommonSerializer):
    annotations: AnnotationsSerializer = field()

class IdentifiableSerializer(AnnotableSerializer):
    object_id: str = field(is_attribute=True, localname='id')
    urn: str = field(is_attribute=True)
    uri: str = field(is_attribute=True)

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if not self._instance: return
        self.urn = self.make_urn()
        self.uri = self.make_uri()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.object_id == other.object_id

    def make_urn(self):
        pass

    def make_uri(self):
        pass

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if not obj.object_id:
            obj.object_id = self.object_id
        return obj

class NameableSerializer(IdentifiableSerializer):

    name: Iterable[TextSerializer] = field(namespace_key='common', related_name='name')
    description: Iterable[TextSerializer] = field(namespace_key='common', related_name='description')

    def get_item_set(self, related_name):
        return self._instance.text.filter(text_type=related_name) 


class VersionableSerializer(NameableSerializer):
    version: str = field(is_attribute=True, default='1.0')
    valid_from: datetime = field(is_attribute=True)
    valid_to: datetime = field(is_attribute=True)

    def __post_init__(self):
        self.version = list(map(int, self.version)) 

    def __eq__(self, other):
        if not super().__eq__(other): return
        return self.version == other.version

    def __lt__(self, other):
        if not super().__eq__(other): return
        return self.version < other.version

    def __gt__(self, other):
        if not super().__eq__(other): return
        return self.version > other.version

    def __ge__(self, other):
        if not super().__eq__(other): return
        return self.version >= other.version

    def __le__(self, other):
        if not super().__eq__(other): return
        return self.version <= other.version


    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if not obj.version:
            obj.version = self.version
        if not obj.valid_from:
            obj.valid_from = self.valid_from
        if not obj.valid_to:
            obj.valid_to = self.valid_to
        return obj

class MaintainableSerializer(VersionableSerializer):
    agency_id: str = field(is_attribute=True, localname='agencyID',
                           forward=True, forward_accesor='agency__object_id')
    is_final: bool = field(is_attribute=True, default=False)
    is_external_reference: bool = field(is_attribute=True, default=False)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)

    def __eq__(self, other):
        if not super().__eq__(other): return
        return self.agency_id == other.agency_id

    def make_structure_url(self):
        resource = constants.CLASS2RESOURCE(self._meta.name)[0]
        return f'http://www.fiesta.org/{resource}/{self.agency_id}/{self.version}'

    @classmethod
    def generate_restful_many(cls, query):
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
        return context.queries[cls] | Q(**kwargs)

    @classmethod
    def make_related_query(cls, related_cls, context):
        return context.queries[cls]

    @classmethod
    def _make_query_args(cls, context, depth):
        children = cls._meta.get_children()
        references = context.query.references
        qrs = context.queries
        if not depth:
            qrs[cls] = cls.make_root_query(context)
        depth += 1
        if references in ['children', 'parentsandsiblings'] and depth == 1:
            for cld_cls in children:
                qrs[cld_cls] = cld_cls.make_related_query(cls, context)
        elif references in ['descendants', 'all'] and depth >= 1:
            for cld_cls in children:
                qrs[cld_cls] = cld_cls.make_related_query(cls, context)
            for cld_cls in children:
                cld_cls._make_query_args(context, depth)
        elif references in constants.RESOURCES:
            for item in constants.RESOURCE2MAINTAINABLE[references]:
                cld_cls = cls._meta.select_child(item, children)
                if not cld_cls: continue
                qrs[cld_cls] = cld_cls.make_related_query(cls, context)
        if references in ['parents', 'parentsandsiblings', 'all'] and depth == 1:
            for parent in cls._meta.get_parents():
                qrs[parent] = parent.make_related_query(cls, context)

    def as_stub(self, class_meta, detail, resource):
        """Returns True if element should be rendered as stub."""
        return (
            (detail == 'allstubs') 
            or
            ((detail == 'referencestubs') and 
             (resource not in class_meta.resources))
        )

    def extract_maintainable(self, structures):
        maintainables = self._field.name
        structure_container_name = self._container._container._meta.underscore_name
        structure_container = getattr(structures, structure_container_name, None)
        try:
            obj = list(getattr(structure_container, maintainables))[0]
        except (IndexError, KeyError, AttributeError):
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2202_PULLED_NO_CONTENT_STRUCTURE) 
        else:
            return obj

    def get_external_maintainable(self):
        location = self.structure_url
        if not location:
            self._context.result.status_message.update(
                'Failure',
                status.FIESTA_2103_SOAP_PULLING_NOT_IMPLEMENTED
            ) 
            return
        header = self.create_structure_header()
        message = ExternalRequest(header).get(location)
        if not isinstance(message, StructureSerializer):
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2201_PULLED_NOT_STRUCTURE
            ) 
            return
        obj = self.extract_maintainable(message.structures)
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
        ref = MaintainableRefSerializer(
            agency_id=self.agency_id,
            object_id=self.object_id,
            version=self.version,
            cls=self._meta.class_name,
            package=self._meta.app
        )
        reference =  MaintainableReferenceSerializer(ref=ref)
        reference.durn = reference.make_maintainable_urn()
        return reference

    def to_submission_result(self):
        reference = self.to_reference()
        submitted_structure = SubmittedStructureSerializer(
            maintainable_object=reference, 
            action=self._context.action, 
            external_dependencies=self._context.external_dependencies
        )
        submission_result = submitted_structure.to_result()
        submission_result._container = self._container._container
        return submission_result

    def process_prevalidate(self):
        self._context.result = self.get_or_add_result(self.to_submission_result())
        model = apps.get_model('base', 'agency')
        try:
            self.agency = model.objects.get(object_id=self.agency_id)
        except model.DoesNotExist:
            self._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2403_AGENCY_NOT_REGISTERED,
            )
            self._stop = True

    def process_premake(self):
        if self.is_external_reference:
            sdmxobj = self.get_external_maintainable()
            if not sdmxobj:
                self._stop = True
                return
            self = sdmxobj
        obj, created = self._meta.model.objects.get_or_create(
            agency=self.agency,
            object_id=self.object_id,
            version=self.version
        )
        self._created = created
        return obj 

    def process_validate(self, obj):
        action = self._result.submitted_structure.action
        if action == 'Delete':
            if obj.is_final:
                self._context.result.status_message.update(
                    'Failure',
                    status.FIESTA_2101_MODIFICATION_NOT_ALLOWED
                ) 
                self._stop = True
            else:
                try:
                    obj.delete()
                except ProtectedError:
                    self._context.result.status_message.update(
                        'Failure',
                        status.FIESTA_2104_PROTECTED
                    ) 
                else:
                    self._context.result.status_message.update(
                        'Success',
                    ) 
                self._stop = True
        elif action == 'Update':
            if not self._created:
                self._context.result.status_message.update(
                    'Failure',
                    status.FIESTA_2102_APPENDING_NOT_ALLOWED,
                )
                self._stop = True

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if not obj.is_final:
            obj.is_final = self.is_final
        self._context.result.status_message.update('Success')
        obj.submitted_structure.add(self._context.result.process(context=self._context))
        return obj

class ItemSchemeSerializer(MaintainableSerializer):
    is_partial: bool = field(is_attribute=True, default=False)

    @cached_property
    def items_as_dict(self):
        items = {i.object_id : i for i in self.items}
        self.items = items
        return self.items
    
    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, name):
        return self.items_as_dict[name]

    def __iter__(self):
        if not isinstance(self.items, dict):
            return self.items
        return iter(self.items.values())

    def __len__(self):
        return len(self.items_as_dict)

    def __contains__(self, item):
        return item in self.items_as_dict.values()

    def __eq__(self, other):
        if not super().__eq__(other): return
        if self.is_partial or other.is_partial: return
        return set(self.items_as_dict) == set(other.items_as_dict)

    def __le__(self, other):
        if not super().__le__(other): return
        if self.is_partial or other.is_partial: return
        return set(self.items_as_dict) <= set(other.items_as_dict)

    def __lt__(self, other):
        if not super().__le__(other): return
        if self.is_partial or other.is_partial: return
        return set(self.items_as_dict) < set(other.items_as_dict)

    def __gt__(self, other):
        if not super().__le__(other): return
        if self.is_partial or other.is_partial: return
        return set(self.items_as_dict) > set(other.items_as_dict)

    def __ge__(self, other):
        if not super().__le__(other): return
        if self.is_partial or other.is_partial: return
        return set(self.items_as_dict) >= set(other.items_as_dict)

    def __sub__(self, other):
        if not self >= other: return
        sub = self.copy()
        sub.items = [i for i in self if i not in other]


class ItemWithParentSchemeSerializer(ItemSchemeSerializer):

    def __eq__(self, other):
        if not super().__eq__(other): return
        for key, val in self.items_as_dict.items():
            if not val == other.items_as_dict[key]: return 
        return True

    def __le__(self, other):
        if not super().__le__(other): return
        for key, val in self.items_as_dict.items():
            if not val == other.items_as_dict[key]: return 
        return True

    def __lt__(self, other):
        if not super().__lt__(other): return
        for key, val in self.items_as_dict.items():
            if not val == other.items_as_dict[key]: return 
        return True

    def __gt__(self, other):
        if not super().__gt__(other): return
        for key, val in other.items_as_dict.items():
            if not val == self.items_as_dict[key]: return 
        return True

    def __ge__(self, other):
        if not super().__ge__(other): return
        for key, val in other.items_as_dict.items():
            if not val == self.items_as_dict[key]: return 
        return True


class StructuresItemsSerializer(Serializer):

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
            if maintainable_type not in context.queries: continue
            query = context.queries[maintainable_type]
            setattr(self, f.name, maintainable_type.generate_restful_many(query))

class ItemSerializer(NameableSerializer):
    pass

class ItemWithParentSerializer(ItemSerializer):
    parent: LocalReferenceSerializer = field(namespace_key='common')

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if self._instance:
            parent = self._instance.get_parent()
            self.parent = LocalReferenceSerializer(parent)

    def __eq__(self, other):
        if not super().__eq__(other): return
        return self.parent == other.parent
        

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


class AgencySerializer(ItemSerializer):
    contact: List[ContactSerializer] = field()

    class Meta:
        app_name = 'base'
        model_name = 'agency'
        namespace_key = 'structure'

    def __post_init(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if self._instance:
            self.object_id = self.extract_object_id()

    def extract_object_id(self):
        if not '.' in self.object_id: return self.object_id
        return self.object_id.split('.')[-1]

class DataProviderContactTelephoneSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'dataprovidercontacttelephone'


class DataProviderContactFaxSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'dataprovidercontactfax'

class DataProviderContactX400Serializer(SimpleStringContactSerializer):
    pass

    class Meta:
        app_name = 'base'
        model_name = 'dataprovidercontactx400'

class DataProviderContactURISerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'dataprovidercontacturi'

class DataProviderContactEmailSerializer(SimpleStringContactSerializer):
    class Meta:
        app_name = 'base'
        model_name = 'dataprovidercontactemail'

class DataProviderContactSerializer(BaseContactSerializer):
    telephone: Iterable[DataProviderContactTelephoneSerializer] = field(forward_accesor='dataprovidercontacttelephone_set')
    fax: Iterable[DataProviderContactFaxSerializer] = field(forward_accesor='dataprovidercontactfax_set')
    x400: Iterable[DataProviderContactX400Serializer] = field(forward_accesor='dataprovidercontactx400_set')
    uri: Iterable[DataProviderContactURISerializer] = field(localname='URI', forward_accesor='dataprovidercontacturi_set')
    email: Iterable[DataProviderContactEmailSerializer] = field(forward_accesor='dataprovidercontactemail_set')

    class Meta:
        app_name = 'base'
        model_name = 'dataprovidercontact'
        namespace_key = 'message'

class DataProviderSerializer(ItemSerializer):
    contact: Iterable[DataProviderContactSerializer] = field(forward_accesor='dataprovidercontact_set')

    class Meta:
        app_name = 'base'
        model_name = 'dataprovider'
        namespace_key = 'structure'

class DataConsumerContactTelephoneSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumercontacttelephone'


class DataConsumerContactFaxSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumercontactfax'

class DataConsumerContactX400Serializer(SimpleStringContactSerializer):
    pass

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumercontactx400'

class DataConsumerContactURISerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumercontacturi'

class DataConsumerContactEmailSerializer(SimpleStringContactSerializer):
    class Meta:
        app_name = 'base'
        model_name = 'dataconsumercontactemail'

class DataConsumerContactSerializer(BaseContactSerializer):
    telephone: Iterable[DataConsumerContactTelephoneSerializer] = field(forward_accesor='dataconsumercontacttelephone_set')
    fax: Iterable[DataConsumerContactFaxSerializer] = field(forward_accesor='dataconsumercontactfax_set')
    x400: Iterable[DataConsumerContactX400Serializer] = field(forward_accesor='dataconsumercontactx400_set')
    uri: Iterable[DataConsumerContactURISerializer] = field(localname='URI', forward_accesor='dataconsumercontacturi_set')
    email: Iterable[DataConsumerContactEmailSerializer] = field(forward_accesor='dataconsumercontactemail_set')

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumercontact'
        namespace_key = 'message'

class DataConsumerSerializer(ItemSerializer):
    contact: Iterable[DataConsumerContactSerializer] = field(forward_accesor='dataconsumercontact_set')

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumer'
        namespace_key = 'structure'

class OrganisationUnitContactTelephoneSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'organisationunitcontacttelephone'


class OrganisationUnitContactFaxSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'organisationunitcontactfax'

class OrganisationUnitContactX400Serializer(SimpleStringContactSerializer):
    pass

    class Meta:
        app_name = 'base'
        model_name = 'organisationunitcontactx400'

class OrganisationUnitContactURISerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'base'
        model_name = 'organisationunitcontacturi'

class OrganisationUnitContactEmailSerializer(SimpleStringContactSerializer):
    class Meta:
        app_name = 'base'
        model_name = 'organisationunitcontactemail'

class OrganisationUnitContactSerializer(BaseContactSerializer):
    telephone: Iterable[OrganisationUnitContactTelephoneSerializer] = field(forward_accesor='organisationunitcontacttelephone_set')
    fax: Iterable[OrganisationUnitContactFaxSerializer] = field(forward_accesor='organisationunitcontactfax_set')
    x400: Iterable[OrganisationUnitContactX400Serializer] = field(forward_accesor='organisationunitcontactx400_set')
    uri: Iterable[OrganisationUnitContactURISerializer] = field(localname='URI', forward_accesor='organisationunitcontacturi_set')
    email: Iterable[OrganisationUnitContactEmailSerializer] = field(forward_accesor='organisationunitcontactemail_set')

    class Meta:
        app_name = 'base'
        model_name = 'organisationunitcontact'
        namespace_key = 'message'

class OrganisationUnitSerializer(ItemWithParentSerializer):
    contact: Iterable[OrganisationUnitContactSerializer] = field(forward_accesor='organisationunitcontact_set')

    class Meta:
        app_name = 'base'
        model_name = 'organisationunit'
        namespace_key = 'structure'

class AgencySchemeSerializer(ItemSchemeSerializer):
    items: Iterable[AgencySerializer] = field(localname='agency') 

    class Meta:
        app_name = 'base'
        model_name = 'agency'
        namespace_key = 'structure'
        structures_field_name = 'organisation_schemes'

    def __post_init__(self, *args, **kwargs):
        super.__post_init__(*args, **kwargs)
        if self._instance:
            self.description = None
            self.annotations = None
            self.name = (
                TextSerializer(lang=lang, text=f"{self.object_id} {_('Agency scheme')}") for lang in settings.LANGUAGES
            )
            if self.object_id == 'SDMX':
                self.agency = (
                    AgencySerializer(instance) for instance in self._meta.model.get_rood_nodes() 
                )
            else:
                self.agency = (
                    AgencySerializer(instance) for instance in self._instance.get_children()
                )

    @classmethod
    def make_root_query(cls, context):
        root = super().make_root_query(context)
        root_args = dict(*root.children)
        resource_id = root_args.get('object_id')
        if resource_id and resource_id != 'AGENCIES':
            raise ParseError('The resourceID of an agencyscheme query must be equal to AGENCIES if set')
        else: root = root & Q(object_id='AGENCIES')
        return root

        
class DataProviderSchemeSerializer(MaintainableSerializer):
    data_provider: Iterable[DataProviderSerializer] = field(forward_accesor='dataprovider_set') 

    class Meta:
        app_name = 'base'
        model_name = 'dataproviderscheme'
        namespace_key = 'structure'
        structures_field_name = 'organisation_schemes'
        parents_names = ['ProvisionAgreementSerializer', 'ContentConstraintSerializer']

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'ProvisionAgreementSerializer':
            qlist.append(Q(organisation__provisionagreement__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ContentConstraintSerializer':
            qlist.append(Q(organisation__contentconstraint__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

    @classmethod
    def make_root_query(cls, context):
        root = super().make_root_query(context)
        root_args = dict(*root.children)
        resource_id = root_args.get('object_id')
        if resource_id and resource_id != 'DATA_PROVIDERS':
            raise ParseError('The resourceID of a dataproviderscheme query must be equal to DATA_PROVIDERS if set')
        else: root = root & Q(object_id='DATA_PROVIDERS')
        return root

class DataConsumerSchemeSerializer(MaintainableSerializer):
    data_consumer: Iterable[DataConsumerSerializer] = field(forward_accesor='dataconsumer_set') 

    class Meta:
        app_name = 'base'
        model_name = 'dataconsumerscheme'
        namespace_key = 'structure'
        structures_field_name = 'organisation_schemes'
    @classmethod
    def make_root_query(cls, context):
        root = super().make_root_query(context)
        root_args = dict(*root.children)
        resource_id = root_args.get('object_id')
        if resource_id and resource_id != 'DATA_CONSUMERS':
            raise ParseError('The resourceID of an dataconsumerscheme query must be equal to DATA_CONSUMERS if set')
        else: root = root & Q(object_id='DATA_CONSUMERS')
        return root


class OrganisationUnitSchemeSerializer(ItemWithParentSchemeSerializer):
    items: Iterable[OrganisationUnitSerializer] = field(localname='OrganisationUnit', namespace_key='structure') 

class OrganisationSchemesSerializer(StructuresItemsSerializer):
    agency_scheme: Iterable[AgencySchemeSerializer] = field()
    data_consumer_scheme: Iterable[DataConsumerSchemeSerializer] = field()
    data_provider_scheme: Iterable[DataProviderSchemeSerializer] = field()
    organisation_unit_scheme: Iterable[OrganisationUnitSchemeSerializer] = field()

    class Meta:
        app_name = 'base'
        namespace_key = 'structure'

class TelephoneSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'registry'
        model_name = 'telephone'

class FaxSerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'registry'
        model_name = 'fax'

class X400Serializer(SimpleStringContactSerializer):
    pass

    class Meta:
        app_name = 'registry'
        model_name = 'x400'

class URISerializer(SimpleStringContactSerializer):

    class Meta:
        app_name = 'registry'
        model_name = 'uri'

class EmailSerializer(SimpleStringContactSerializer):
    class Meta:
        app_name = 'registry'
        model_name = 'email'

class ContactSerializer(BaseContactSerializer):
    telephone: Iterable[TelephoneSerializer] = field()
    fax: Iterable[FaxSerializer] = field()
    x400: Iterable[X400Serializer] = field()
    uri: Iterable[URISerializer] = field(localname='URI')
    email: Iterable[EmailSerializer] = field()

    class Meta:
        app_name = 'registry'
        model_name = 'contact'
        namespace_key = 'message'

class HeaderContactSerializer(BaseContactSerializer):

    def process_premake(self):
        return self._meta.model.objects.create(
            party=self._container._obj
        )

    def process_postmake(self, obj):
        for f in ['name', 'department', 'role']: 
            self.update_translateable(obj, f)


class PartySerializer(Serializer):

    name: Iterable[TextSerializer] = field(namespace_key='common')
    contact: Iterable[HeaderContactSerializer] = field()
    object_id: str = field(is_attribute=True, localname='id')
    timezone: str = field(namespace_key='message')

    class Meta:
        app_name = 'base'
        model_name = 'Party'
        namespace_key = 'message'

    def process_premake(self):
        obj = self._meta.model.objects.create(
            object_id=self.object_id,
            timezone=self.timezone
        )
        self.update_translateable(obj, 'name')
        return obj

    def wsrest_party(self, registration):
        if isinstance(registration.user, AnonymousUser):
            self.object_id='not_supplied'
            return
        contact = HeaderContactSerializer(email=[registration.user.username])
        receiver = registration.user.contact.organisation
        self.object_id = receiver.object_id
        self.contact = [contact]

    def wsrest_sender(self):
        self.object_id = api_settings.DEFAULT_SENDER_ID 


class PayloadStructureSerializer(Serializer):
    provision_agreement: ReferenceSerializer = field()
    structure_usage: ReferenceSerializer = field()
    structure: ReferenceSerializer = field()
    structure_id: str = field(is_attribute=True, localname='structureID')
    schema_url: str = field(is_attribute=True, localname='schemaURL')
    namespace: str = field(is_attribute=True)
    dimension_at_observation: str = field(is_attribute=True)
    explicit_measures: str = field(is_attribute=True)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)


    class Meta:
        app_name = 'registry'
        model_name = 'PayloadStructure'
        namespace_key = 'common'

class HeaderSerializer(Serializer):
    object_id: str = field(localname='ID')
    test: bool = field(default=False)
    prepared: datetime = field()
    sender: PartySerializer = field()
    receiver: PartySerializer = field()
    name: Iterable[TextSerializer] = field(namespace_key='common')
    structure: Iterable[PayloadStructureSerializer] = field()
    data_provider: ItemReferenceSerializer = field()
    data_set_action: str = field()
    data_set_id: str = field(localname='DataSetID')
    extracted: datetime = field()
    reporting_begin: str = field()
    reporting_end: str = field()
    embargo_date: datetime = field()
    source: str = field()

    class Meta:
        app_name = 'registry'
        model_name = 'Header'
        namespace_key = 'message'

    def process_postmake(self, obj):
        obj = self._meta.model.objects.create(
            log=self._context.log,
            object_id=self.object_id,
            test=self.test,
            prepared=self.prepared,
            sender=self.m_sender,
            receiver=self.m_receiver,
        )
        self._sid = transaction.savepoint()
        return obj

    def to_response(self):
        header = HeaderSerializer(
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
        self.sender=PartySerializer().wsrest_sender(),
        self.receiver=PartySerializer().wsrest_party(log.restful_query),


class CodeSerializer(ItemWithParentSerializer):

    class Meta:
        app_name = 'codelist'
        model_name = 'code'
        namespace_key = 'structure'

class CodelistSerializer(ItemWithParentSchemeSerializer):
    items: Iterable[CodeSerializer] = field(localname='Code') 

    class Meta:
        app_name ='codelist'
        model_name = 'codelist'
        namespace_key = 'structure'
        structures_field_name = 'codelists'
        parents_names = ['ConceptSchemeSerializer', 'DataStructureSerializer']

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'ConceptSchemeSerializer':
            qlist.append(Q(representation__concept__wrapper__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'DataStructureSerializer':
            qlist.append(Q(representation__dimension__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
            qlist.append(Q(representation__concept__dimension__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class CodelistsSerializer(StructuresItemsSerializer):
    codelist: Iterable[CodelistSerializer] = field(namespace_key='structure')

class FormatSerializer(Serializer):
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
        app_name ='common'
        # model_name = 'format'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            **asdict(self)
        )
        return obj

class RepresentationSerializer(Serializer):
    text_format: FormatSerializer = field()
    enumeration: MaintainableReferenceSerializer = field()
    enumeration_format: FormatSerializer = field()

    class Meta:
        app_name ='common' 
        model_name = 'representation'
        namespace_key = 'common'

            
    def process_postmake(self):
        enumeration = self.enumeration
        codelist_obj = None
        if enumeration:
            codelist_model = apps.get_model('codelist', 'Codelist')
            codelist_obj = codelist_model.get_from_ref(enumeration)
            if enumeration._stop: 
                self._stop = True
                return
        obj, _ = self._meta.model.objects.get_or_create(
            text_format=self.m_text_format,
            enumeration=codelist_obj,
            enumeration_format=self.m_enumeration_format)
        return obj

class ISOConceptReferenceSerializer(Serializer):
    concept_agency: str = field()
    concept_scheme_id: str = field(localname='ConceptSchemeID')
    concept_id: str = field(localname='ConceptID')

    class Meta:
        app_name ='conceptscheme'
        model_name = 'isoconceptreference'
        namespace_key = 'structure'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            **asdict(self))
        return obj

class ConceptSerializer(ItemWithParentSerializer):
    core_representation: RepresentationSerializer = field()
    iso_concept_reference: ISOConceptReferenceSerializer = field(localname='ISOConceptReference')

    class Meta:
        app_name ='conceptscheme'
        model_name = 'concept'
        namespace_key = 'structure'

    def process_postmake(self, obj):
        super().process_postmake(obj)
        if not obj.core_representation:
            obj.core_representation = self.m_core_representation
        if not obj.iso_concept_reference:
            obj.iso_concept_reference = self.m_iso_concept_reference
        obj.save()
        return obj


class ConceptSchemeSerializer(MaintainableSerializer):
    concept: Iterable[ConceptSerializer] = field() 

    class Meta:
        app_name = 'conceptscheme'
        model_name = 'conceptscheme'
        namespace_key = 'structure'
        children_names = 'CodelistSerializer'
        parents_names = ['DataStructureSerializer']
        structures_field_name = 'concepts'

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'DataStructureSerializer':
            # From dimension concept_identity 
            qlist.append(Q(concept__dimension_concept_identity__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
            # From measure dimension local_representation
            qlist.append(Q(dimension__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
            # From dimension concept_roles
            qlist.append(Q(concept__dimension_concept_role__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
            # From primarymeasure 
            qlist.append(Q(concept__primarymeasure__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
            # From attribute concept_identity 
            qlist.append(Q(concept__attribute_concept_identity__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
            # From attribute concept_roles
            qlist.append(Q(concept__attribute_concept_role__wrapper__wrapper__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'CodelistSerializer':
            qlist.append(Q(concept__representation__codelist__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class ConceptsSerializer(StructuresItemsSerializer):
    concept_scheme: Iterable[ConceptSchemeSerializer] = field()

class ComponentSerializer(IdentifiableSerializer):
    concept_identity: ItemReferenceSerializer = field()
    local_representation: RepresentationSerializer = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            object_id = self.object_id,
            wrapper = self._wrapper._obj,
        )
        return obj

    def process_postmake(self, obj):
        obj.concept_identity = self.m_concept_identity,
        obj.local_representation = self.m_local_representation,
        return obj

class DimensionSerializer(ComponentSerializer):
    measure_local_representation: MaintainableReferenceSerializer = field(localname='local_representation') 
    concept_role: Iterable[ItemReferenceSerializer] = field(related_name='concept_role')
    position: int = field(is_attribute=True)
    tipe: str = field(localname='type', is_attribute=True)

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'dimension'

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if lxml.etree.iselement(self._element):
            if not self.tipe:
                if self._meta.tag.localname == 'Dimension':
                    self.tipe = 'Dimension'
                elif self._meta.tag.localname == 'MeasureDimension':
                    self.tipe = 'MeasureDimension'
                else:
                    self.tipe = 'TipeDimension'
        if self._instance:
            self.tipe = self._instance.TYPE_CHOICES[self.tipe]
        if self.tipe == 'MeasureDimension':
            self.local_representation = self.measure_local_representation
            self.measure_local_representation = None
        else:
            self.measure_local_representation = None

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        obj.measure_local_representation = self.m_measure_local_representation
        obj.concept_role.add(*self.m_concept_role)
        obj.position = self.position
        obj.tipe = self.tipe

    def make_element(self, tag, attrib):
        tag = QName(constants.NAMESPACE_MAP['structure'], self.tipe) 
        return lxml.etree.Element(tag, attrib=attrib, nsmap=self._meta.nsmap)

class GroupDimensionSerializer(AnnotableSerializer):
    dimension_reference: LocalReferenceSerializer = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'groupdimension'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            wrapper = self._wrapper._obj,
        )

        return obj

    def process_postmake(self, obj):
        obj = super().process_postmake()
        obj.dimension_reference = self.m_dimension_reference
        return obj

class PrimaryMeasureSerializer(ComponentSerializer):

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'primarymeasure'

class AttributeRelationshipSerializer(Serializer):

    null: EmptySerializer = field(localname='None', default=False)
    dimension: Iterable[LocalReferenceSerializer] = field(related_name='dimension_set')
    attachment_group: Iterable[LocalReferenceSerializer] = field(related_name='attachment_group')
    group: LocalReferenceSerializer = field()
    primary_measure: Iterable[LocalReferenceSerializer] = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'attributerelationship'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            object_id = self.object_id,
            wrapper = self._wrapper._obj,
        )
        return obj

    def process_postmake(self, obj):
        obj = super().process_postmake()
        obj.null = self.m_null
        obj.dimension.add(*self.m_dimension)
        obj.attachment_group.add(*self.m_attachment_group)
        obj.group = self.m_group
        obj.primary_measure = self.m_primary_measure
        return obj

class AttributeSerializer(ComponentSerializer):
    concept_role: Iterable[ItemReferenceSerializer] = field(related_name='concept_role')
    attribute_relationship: AttributeRelationshipSerializer = field(forward_accesor='attributerelationship')
    assignment_status: str = field(is_attribute=True) 

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'attribute'

    def __post_init__(self, *args, **kwargs):
        if self._instance:
            self.assignment_status = self._instance.ASSIGNMENT_STATUS_CHOICES[self.assignment_status]


    def process_postmake(self, obj):
        obj = super().process_postmake()
        obj.concept_role.add(*self.m_concept_role)
        obj.assignment_status = self.assignment_status
        return obj

class ComponentListSerializer(IdentifiableSerializer):

    def process_premake(self):
        obj, _ = self._meta.model.get_or_create(
            data_structure =self._wrapper._obj,
        )
        return obj

class DimensionListSerializer(ComponentListSerializer):

    dimension: Iterable[DimensionSerializer] = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'dimensionlist'

    def get_item_set(self, related_name):
        item_set = super().get_item_set(related_name)
        return item_set.order_by('position')

    def serialize_many_elements(self, field_meta):
        item_type = field_meta.fld.type.__args__[0]
        many = []
        i = 1
        for child_element in self._element:
            if QName(child_element).localname.lower() == 'annotations': continue
            serializer = item_type(child_element, complain=False)
            serializer.position = i
            many.append(serializer)
            i += 1
        return many

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.object_id = 'DimensionDescriptor'

class GroupSerializer(ComponentListSerializer):

    group_dimension: Iterable[GroupDimensionSerializer] = field()
    attachment_constraint: MaintainableReferenceSerializer = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'group'

    def process_premake(self):
        return self._meta.model.get_or_create(
            object_id=self.object_id,
            wrapper=self._wrapper._obj,
        )

class MeasureListSerializer(ComponentListSerializer):
    primary_measure: Iterable[PrimaryMeasureSerializer] = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'measurelist'

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.object_id = 'MeasureDescriptor'

class AttributeListSerializer(ComponentListSerializer):
    attribute: Iterable[AttributeSerializer] = field()

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'
        model_name = 'attributelist'

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.object_id = 'AttributeDescriptor'

class DataStructureComponentsSerializer(Serializer):
    dimension_list: DimensionListSerializer = field(forward_accesor='dimensionlist')
    group: Iterable[GroupSerializer] = field()
    measure_list: MeasureListSerializer = field(forward_accesor='measurelist')
    attribute_list: AttributeListSerializer = field(forward_accesor='attributelist')

    class Meta:
        app_name = 'datastructure'
        namespace_key = 'structure'

class DataStructureSerializer(MaintainableSerializer):
    data_structure_components: DataStructureComponentsSerializer = field()

    class Meta:
        app_name = 'datastructure'
        model_name = 'datastructure'
        namespace_key = 'structure'
        children_names = ['ConceptSchemeSerializer, CodelistSerializer']
        parents_names = ['DataflowSerializer', 'AttachmentConstraintSerializer']
        structures_field_name = 'datastructures'

    def expose_group(self):
        result_list, result_dict = [], {}
        components = self.data_structure_components
        groups = components.group
        if groups: result_list = list(groups.copy())
        result_dict = {group.object_id: group for group in result_list}
        return result_list, result_dict

    def expose_components(self, component_name, component_subname):
        result_list, result_dict = [], {}
        components = getattr(self.data_structure_components, component_name)
        if components: result_list = list(getattr(components, component_subname).copy())
        result_dict = {comp.object_id: comp for comp in result_list}
        return result_list, result_dict

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.dimension_list, self.dimension_dict = self.expose_components('dimension_list', 'dimension')
        self.group_list, self.group_dict = self.expose_group()
        self.measure_list, self.measure_dict = self.expose_components('measure_list', 'primary_measure')
        self.attribute_list, self.attribute_dict = self.expose_components('attribute_list', 'attribute')
        if not self._instance: return
        serializers = import_module(api_settings.DEFAULT_SERIALIZER_MODULE)
        item_set = self._instance.content_constraint
        self.content_constraint_list = [serializers.ContentConstraintSerializer(item) for item in item_set]
        item_set = self._instance.attachment_constraint
        self.attachment_constraint_list = [AttachmentConstraintSerializer(item) for item in item_set]

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'CodelistSerializer':
            # From dimension local_representation 
            qlist.append(Q(dimension_list__dimension__local_representation__codelist__in=rel_objects.filter(rel_qry)))
            # From primary_measure local_representation 
            qlist.append(Q(measure_list__primarymeasure__local_representation__codelist__in=rel_objects.filter(rel_qry)))
            # From attribute local_representation 
            qlist.append(Q(attribute_list__attribute__local_representation__codelist__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ConceptSerializer':
            # From dimension concept_identity and concept_role
            qlist.append(Q(dimension_list__dimension__concept_identity__wrapper__in=rel_objects.filter(rel_qry)))
            qlist.append(Q(dimension_list__dimension__concept_role__wrapper__in=rel_objects.filter(rel_qry)))
            # From primarymeasure concept_identity
            qlist.append(Q(measure_list__primarymeasure__concept_identity__wrapper__in=rel_objects.filter(rel_qry)))
            # From attribute concept_identity and concept_role
            qlist.append(Q(attribute_list__attribute__concept_identity__wrapper__in=rel_objects.filter(rel_qry)))
            qlist.append(Q(attribute_list__attribute__concept_role__wrapper__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'DataflowSerializer':
            qlist.append(Q(dataflow__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'AttachmentConstraintSerializer':
            qlist.append(Q(attachment_constraint__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ContentConstraintSerializer':
            qlist.append(Q(content_constraint__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class DataStructuresSerializer(StructuresItemsSerializer):
    data_structure: Iterable[DataStructureSerializer] = field()

class DataflowSerializer(MaintainableSerializer):
    structure: ReferenceSerializer = field()

    class Meta:
        app_name = 'datastructure'
        model_name = 'dataflow'
        namespace_key = 'structure'
        children_names = 'DataStructureSerializer'
        parents_names = 'ContentConstraintSerializer'
        structures_field_name = 'dataflows'

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if not self._instance: return
        serializers = import_module(api_settings.DEFAULT_SERIALIZER_MODULE)
        item_set = self._instance.content_constraint
        self.content_constraint_list = [serializers.ContentConstraintSerializer(item) for item in item_set]

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'DataStructureSerializer':
            qlist.append(Q(datastructure__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ProvisionAgreementSerializer':
            qlist.append(Q(provision_agreement__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ContentConstraintSerializer':
            qlist.append(Q(content_constraint__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class DataflowsSerializer(StructuresItemsSerializer):
    dataflow : Iterable[DataflowSerializer] = field()

class ProvisionAgreementSerializer(MaintainableSerializer):
    dataflow: ReferenceSerializer = field(localname='StructureUsage')
    data_provider: ReferenceSerializer = field()

    class Meta:
        app_name = 'registry'
        model_name = 'provisionagreement'
        namespace_key = 'structure'
        children_names = ['DataflowSerializer', 'DataProviderSchemeSerializer']
        parents_names = 'ContentConstraintSerializer'
        structures_field_name = 'provision_agreements'

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        if not self._instance: return
        serializers = import_module(api_settings.DEFAULT_SERIALIZER_MODULE)
        item_set = self._instance.content_constraint
        self.content_constraint_list = [serializers.ContentConstraintSerializer(item) for item in item_set]

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'DataflowSerializer':
            qlist.append(Q(dataflow__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'DataProviderSchemeSerializer':
            qlist.append(Q(data_provider__wrapper__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ContentConstraintSerializer':
            qlist.append(Q(content_constraint__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class ProvisionAgreementsSerializer(StructuresItemsSerializer):
    provision_agreement: Iterable[ProvisionAgreementSerializer] = field()

class AttachmentConstraintAttachmentSerializer(Serializer):
    # Attachment constraints not attached to structural metadata (DSD) 
    # are of no use since groups and their association to attachment
    # constraints must be defined in structural metadata (DSD) and be given a unique identifier,
    # thus should be attached to datastructure 

    data_structure: Iterable[MaintainableReferenceSerializer] = field(related_name='datastructure_set', FormatSerializer='data_structures')

    class Meta:
        namespace_key = 'structure'

    def process_postvalidate(self, obj): 
        super().process_postvalidate(obj)
        self.data_structure = list(self.data_structure)
        dsd = self.data_structure[0]
        self._context.dsd = self.get_from_reference(dsd).unroll()
        
    def process_postmake(self, obj):
        obj = super().postmake(obj)
        for attachment in ['data_structure']:
            if getattr(self, attachment):
                setattr(self, attachment, list(getattr(self, attachment)))
                for item in getattr(self, attachment):
                    item._obj.attachment_constraint.add(obj)
        return obj

class ContentConstraintAttachmentSerializer(Serializer):
    #TODO Most likely will never implement content constraints attached to DataSet and SimpleDataSource since I don't see a demand for them
    #TODO Most likely will never implement content constraints attached to Queryable artefacts since SOAP web service is not implemented

    data_provider: ItemReferenceSerializer = field()
    data_structure: Iterable[MaintainableReferenceSerializer] = field(forward_accesor='data_structures')
    dataflow: Iterable[MaintainableReferenceSerializer] = field(forward_accesor='dataflows')
    provision_agreement: Iterable[MaintainableReferenceSerializer] = field(forward_accesor='provision_agreements')

    class Meta:
        namespace_key = 'structure'

    def process_postmake(self, obj):
        obj = super().postmake(obj)
        if self.data_provider:
            self.m_data_provider.add(obj)
        for attachment in ['data_structure', 'dataflow', 'provision_agreement']:
            if getattr(self, attachment):
                setattr(self, attachment, list(getattr(self, attachment)))
                for item in getattr(self, attachment):
                    item._obj.content_constraint.add(obj)
        return obj

class BaseSubKeySerializer(Serializer):
    value: StringSerializer = field()

class SubKeySerializer(BaseSubKeySerializer):
    component_id: str = field(is_attribute=True, localname='id')

    class Meta:
        app_name = 'registry'
        model_name = 'subkey'
        namespace_key = 'common'

    def process_postmake(self):
        return self._meta.model.objects.create(
            key=self._wrapper._obj,
            component_id=self.component_id,
            value=self.value.text
        )

class CubeRegionKeyValueSerializer(BaseSubKeySerializer):

    class Meta:
        app_name = 'registry'
        model_name = 'cuberegionkeyvalue'
        namespace_key = 'common'

    def process_postmake(self):
        return self._meta.model.objects.create(
            key=self._wrapper._obj,
            value=self.value.text
        )

class KeySerializer(Serializer):
    sub_key: Iterable[SubKeySerializer] = field(forward_accesor='subkey_set')

    class Meta:
        app_name = 'registry'
        model_name = 'key'
        namespace_key = 'structure'

    def process_premake(self):
        return self._meta.model.objects.create(
            key_set=self._wrapper._obj,
        )

class TimePeriodSerializer(StringSerializer):
    time_period: str = field(is_text=True)
    is_inclusive: bool = field(is_attribute=True, default=True)

    class Meta:
        app_name = 'registry'
        model_name = 'timeperiod'
        namespace_key = 'structure'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            time_period=self.text,
            is_inclusive=self.inclusive
        )
        return obj

class TimeRangeSerializer(CommonSerializer):
    before_period: TimePeriodSerializer = field() 
    after_period: TimePeriodSerializer = field()
    start_period: TimePeriodSerializer = field()
    end_period: TimePeriodSerializer = field()

    def process_postmake(self, obj):
        before_period = self.m_before_period if self.before_period else None 
        after_period = self.m_after_period if self.after_period else None 
        start_period = self.m_start_period if self.start_period else None 
        end_period = self.m_end_period if self.end_period else None 
        obj, _ = self._meta.model.objects.get_or_create(
            cube_region_key=self._wrapper._obj,
            before_period=before_period,
            after_period=after_period,
            start_period=start_period,
            end_period=end_period,
        )
        return obj

class CubeRegionKeySerializer(Serializer):
    component_id: str = field(is_attribute=True, localname='id')
    value: Iterable[ValueSerializer] = field(forward_accesor='cuberegionkeyvalue_set')
    time_range: TimeRangeSerializer = field(forward_accesor='cuberegionkeytimerange')

    class Meta:
        app_name = 'registry'
        model_name = 'cuberegionkey'
        namespace_key = 'common'

    def process_postmake(self):
        return self._meta.model.objects.create(
            cube_region=self._wrapper._obj,
            component_id=self.component_id,
        )

class DataKeySetSerializer(Serializer):
    key: Iterable[KeySerializer] = field()
    is_included: bool = field(is_attribute=True)

    class Meta:
        app_name = 'registry'
        model_name = 'keyset'
        namespace_key = 'structure'

    def process_premake(self):
        if self._wrapper._meta.object_name == 'AttachmentConstraintSerializer':
            return self._meta.model.objects.create(
                attachment_constraint=self._wrapper._obj,
                is_included=self.is_included
            )
        else:
            return self._meta.model.objects.create(
                content_constraint=self._wrapper._obj,
                is_included=self.is_included
            )

class CubeRegionSerializer(Serializer):
    key_value: Iterable[CubeRegionKeySerializer] = field(forward_accesor='key_value_set') 
    attribute: Iterable[CubeRegionKeySerializer] = field(forward_accesor='attribute_set') 
    include: bool = field(is_attribute=True, default=True)

    class Meta:
        app_name = 'registry'
        model_name = 'cuberegion'
        namespace_key = 'common'

    def process_premake(self):
        return self._meta.model.objects.create(
            content_constraint=self._wrapper._obj,
            include=self.include
        )

class AttachmentConstraintSerializer(MaintainableSerializer):
    constraint_attachment: AttachmentConstraintAttachmentSerializer = field()
    data_key_set: Iterable[DataKeySetSerializer] = field(forward_accesor='keyset_set')

    class Meta:
        app_name = 'registry'
        model_name = 'attachmentconstraint'
        namespace_key = 'structure'
        children_names = 'DataStructureSerializer'
        structures_field_name = 'constraints'

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'DataStructureSerializer':
            qlist.append(Q(datastructure__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class ReleaseCalendarSerializer(Serializer):
    periodicity: StringSerializer = field(is_text=True)
    offset: StringSerializer = field(is_text=True)
    tolerance: StringSerializer = field(is_text=True)

    class Meta:
        app_name = 'registry'
        model_name = 'releasecalendar'
        namespace_key = 'structure'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            periodicity=self.periodicity,
            offset=self.offset,
            tolerance=self.tolerance
        )
        return obj

class ReferencePeriodSerializer(Serializer):
    start_time: datetime = field()
    end_time: datetime = field()

    class Meta:
        app_name = 'common'
        model_name = 'referenceperiod'
        namespace_key = 'common'

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            start_time = self.start_time,
            end_time = self.end_time
        )
        return obj

class ContentConstraintSerializer(MaintainableSerializer):
    constraint_attachment: ContentConstraintAttachmentSerializer = field()
    data_key_set: Iterable[DataKeySetSerializer] = field(forward_accesor='keyset_set')
    cube_region: Iterable[CubeRegionSerializer] = field(forward_accesor='cuberegion_set') 
    release_calendar: ReleaseCalendarSerializer = field()
    reference_period: ReferencePeriodSerializer = field()
    tipe: str = field(localname='type', is_attribute=True, default='Actual')

    class Meta:
        app_name = 'registry'
        model_name = 'contentconstraint'
        namespace_key = 'structure'
        children_names = ['DataProviderSchemeSerializer',
                          'DataStructureSerializer', 'DataflowSerializer',
                          'ProvisionAgreementsSerializer']
        structures_field_name = 'constraints'

    def process_postmake(self, obj):
        obj = super().process_postmake(obj)
        if self.release_calendar:
            obj.release_calendar = self.m_release_calendar
        if self.reference_period:
            obj.reference_period = self.m_reference_period
        obj.tipe = self.tipe
        return obj

    @classmethod
    def make_related_query(cls, related_cls, context):
        qlist = []
        qrs = context.queries
        qlist.append(qrs[cls])
        rel_qry = qrs[related_cls]
        rel_objects = related_cls._meta.model.objects
        if related_cls._meta.object_name == 'DataStructureSerializer':
            qlist.append(Q(datastructure__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'DataflowSerializer':
            qlist.append(Q(dataflow__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'ProvisionAgreementSerializer':
            qlist.append(Q(provisionagreement__in=rel_objects.filter(rel_qry)))
        elif related_cls._meta.object_name == 'DataProviderSchemeSerializer':
            qlist.append(Q(organisation__wrappers__in=rel_objects.filter(rel_qry)))
        return functools.reduce(lambda x, y: x | y, qlist)

class ConstraintsSerializer(StructuresItemsSerializer):
    attachment_constraint: Iterable[AttachmentConstraintSerializer] = field()
    content_constraint: Iterable[ContentConstraintSerializer] = field()


class StructuresSerializer(Serializer):
    organisation_schemes: OrganisationSchemesSerializer = field()
    dataflows: DataflowsSerializer = field()
    # metadataflows: MetadataflowsSerializer = field(namespace_key='registry')
    # category_schemes: CategorySchemesSerializer = field(namespace_key='registry')
    # categorisations: CategorisationsSerializer = field(namespace_key='registry')
    codelists: CodelistsSerializer = field()
    # hierarchical_codelists: HierarchicalCodelistsSerializer = field(namespace_key='registry')
    concepts: ConceptsSerializer = field()
    # metadata_structures: MetadataStructuresSerializer = field(namespace_key='registry')
    data_structures: DataStructuresSerializer = field()
    # structure_sets: StructureSetsSerializer = field(namespace_key='registry')
    # reporting_taxonomies: ReportingTaxonomiesSerializer = field(namespace_key='registry')
    # processes: ProcessesSerializer = field(namespace_key='registry')
    constraints: ConstraintsSerializer = field(namespace_key='registry')
    provision_agreements: ProvisionAgreementsSerializer = field(namespace_key='registry')

    class Meta:
        namespace_key = 'structure'

    def expose_maintainables(self, field_name, subfield_name):
        result_list = []
        field = getattr(self, field_name)
        if field: subfield = getattr(field, subfield_name)
        if subfield:  result_list = list(subfield.copy())
        result_dict = {}
        for m in result_list:
            version = '' if m.version == '1.0' else m.version
            result_dict[f'{m.agency_id}.{m.object_id}.{version}'] = m
        return result_list, result_dict

    def expose_maintainables_asdict(self, field_name, subfield_name):
        value = []
        field = getattr(self, field_name)
        if field: subfield = getattr(field, subfield_name)
        if subfield:  value = list(subfield.copy())
        return value

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        # Expose maintainable lists higher up as lists and as dict
        for fld in self._meta.fields:
            for subfld in field._meta.fields:
                maintainable_list, maintainable_dict = self.expose(fld.name, subfld.name)
                setattr(self, f'{subfld.name}_list', maintainable_list)
                setattr(self, f'{subfld.name}_dict', maintainable_dict)
        
    def retrieve_restful(self, context):
        for f in self._meta.fields:
            if f.name not in context.structures_field_names: continue
            f.type._make_query_args(context)
        for f in self._meta.fields:
            if f.name not in context.all_structures: continue
            value = f.type()
            value.retrieve_restful(context)
            setattr(self, f.name, value)

class FooterMessageSerializer(Serializer):

    text: Iterable[TextSerializer] = field(namespace_key='common')
    code: str = field(is_attribute=True)
    severity: str = field(is_attribute=True)

    class Meta:
        namespace_key = 'common'

class FooterSerializer(Serializer):
    message: Iterable[FooterMessageSerializer] = field()

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

class BaseSDMXMessageSerializer(Serializer):
    header: HeaderSerializer = field()
    footer: FooterSerializer = field(namespace_key='footer')

    class Meta:
        namespace_key = 'message'

class StructureSerializer(BaseSDMXMessageSerializer):
    structures: StructuresSerializer = field()

    def to_request(self):
        submit_structure_request = SubmitStructureRequestSerializer(
            structures=self.structures,
            action='Replace',
            external_dependencies=True
        ) 
        sender = PartySerializer(object_id='ECB')
        receiver = PartySerializer(object_id='FIESTA')
        header = HeaderSerializer(
            object_id='SID1',
            test=False,
            prepared=datetime.now(),
            sender=sender,
            receiver=receiver
        )
        return RegistryInterfaceSubmitStructureRequestSerializer(
            header=header,
            submit_structure_request=submit_structure_request
        )

    def retrieve_restful(self, context):
        self.structures = StructuresSerializer().retrieve_restful(context)
        self.header = HeaderSerializer().to_structure(context.log.restful_query)

class SubmittedStructureSerializer(RegistrySerializer):
    maintainable_object: MaintainableReferenceSerializer = field()
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True)

    def to_result(self):
        new_self = self.__class__(
            maintainable_object=self.maintainable_object,
            action=self.action or self._context.action,
            external_dependencies=self.external_dependencies or self._context.external_dependencies
        )
        return SubmissionResultSerializer(
            submitted_structure=new_self,
            status_message=StatusMessageSerializer()
        )

class SubmitStructureRequestSerializer(Serializer):
    structure_location: str = field() 
    structures: StructuresSerializer = field()
    submitted_structure: Iterable[SubmittedStructureSerializer] = field(forward_accesor='submittedstructure')
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True) 

    class Meta:
        app_name ='registry'
        model_name = 'submitstructurerequest'
        namespace_key = 'registry'

    def __post_init__(self, *args, **kwargs):
        if self._instance:
            self.action = self._instance.ACTION_CHOICES[self.action]


    def process_prevalidate(self):
        if not self.structures:
            header = self.create_structure_header()
            try:
                external_request = ExternalRequest(header)
            except ExternalError:
                self.m_header.delete()
                raise
            structure = external_request.get(self.structure_location)
            if not isinstance(structure, StructureSerializer):
                self.m_header.delete()
                raise ExternalError(
                    _('The message extracted from {} is not a structure message').format(self.structure_location)
                )
            else:
                self.structures = structure.structures
        self._context.action = self.action
        self._context.external_dependencies = self.external_dependencies
        for submitted_structure in self.submitted_structure:
            self._context.get_or_add_result(submitted_structure.to_result())

    def process_premake(self):
        obj = self._meta.model.objects.create(
            submission=self._wrapper.m_header,
            structure_location=self.structure_location,
            action=self._model.ACTION_CHOICES[self.action],
            external_dependencies=self.external_dependencies
        )
        return obj

    def to_response(self):
        return SubmitStructureResponseSerializer(
            submission_result = self._context.generate_result()
        )

class StatusMessageTextSerializer(TextSerializer):
    text: Iterable[TextSerializer] = field(namespace_key='common')
    code: str = field(is_attribute=True)

    def process_premake(self):
        obj, _ = self._meta.model.objects.get_or_create(
            code = self.code 
        )
        return obj

class StatusMessageSerializer(Serializer):
    message_text: Iterable[StatusMessageTextSerializer] = field()
    status: str = field(is_attribute=True)

    class Meta:
        app_name ='registry'
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
            text = [TextSerializer(language, text_entry)]
        self.message_text.append(StatusMessageTextSerializer(text=text, code=message.code))

class SubmissionResultSerializer(Serializer):
    submitted_structure: SubmittedStructureSerializer = field()
    status_message: StatusMessageSerializer = field()

    class Meta:
        app_name ='registry'
        model_name = 'SubmittedStructure'
        namespace_key = 'registry'

    def process_premake(self):
        return self._meta.model.objects.create(
            structure_submission=self._wrapper._obj,
            action = self._context.result.submitted_structure.action,
            external_dependencies = self._context.result.submitted_structure.external_dependencies,
        )

    def process_postmake(self, obj):
        obj.status_message = self.m_status_message
        return obj

class SubmitStructureResponseSerializer(RegistrySerializer):
    submission_result: Iterable[SubmissionResultSerializer] = field()

class NotificationURLSerializer(RegistrySerializer):
    is_soap: str = field(localname='isSOAP', is_attribute=True)
    notification_url: str = field(is_text=True)

class ValidityPeriodSerializer(RegistrySerializer):
    start_date: date = field()
    end_date: date = field()

class IdentifiableObjectEventSerializer(RegistrySerializer):
    all_instances: EmptySerializer = field(localname='All', default=False)
    urn: str = field(localname='URN')
    object_id: str = field(localname='ID', default='%')

class VersionableObjectEventSerializer(IdentifiableObjectEventSerializer):
    version: str = field(default='%')

class StructuralRepositoryEventsSerializer(RegistrySerializer):
    agency_id: Iterable[StringSerializer] = field(namespace_key='registry', localname='AgencyID', default='%')
    all_events: EmptySerializer = field(namespace_key='registry', default=False)
    agency_scheme: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    data_consumer_scheme: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    data_provider_scheme: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    organisation_unit_scheme: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    dataflow: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    metadataflow: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    category_scheme: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    categorisation: Iterable[IdentifiableObjectEventSerializer] = field(namespace_key='registry')
    codelist: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    hierarchical_codelist: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    concept_scheme: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    metadata_structure_definition: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    key_family: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    structure_set: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    reporting_taxonomy: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    process: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    attachment_constraint: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    content_constraint: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    provision_agreement: Iterable[VersionableObjectEventSerializer] = field(namespace_key='registry')
    event_type: str = field(is_attribute=True, localname='TYPE', default='STRUCTURE')

class EventSelectorSerializer(RegistrySerializer):
    structural_repository_events: StructuralRepositoryEventsSerializer = field()
    # data_registration_events: DataRegistrationEvents = field(namespace_key='registry')
    # metadata_registration_events: MetadataRegistrationEvents = field(namespace_key='registry')

class SubscriptionSerializer(RegistrySerializer):
    organisation: ReferenceSerializer = field()
    registry_urn: str = field(localname='RegistryURN')
    notification_mail_to: Iterable[NotificationURLSerializer] = field()
    notification_http: Iterable[NotificationURLSerializer] = field(localname='NotificationHTTP')
    subscriber_assigned_id: str = field(localname='SubscriberAssignedID')
    validity_period: ValidityPeriodSerializer = field()
    event_selector: EventSelectorSerializer = field() 
    action: str = field(is_attribute=True)

class SubmitSubscriptionsRequestSerializer(RegistrySerializer):
    subscription_request: Iterable[SubscriptionSerializer] = field()

class SubscriptionStatusSerializer(RegistrySerializer):
    subscription_urn: str = field(localname='SubscriptionURN')
    subscriber_assigned_id: str = field(localname='SubscriberAssignedID')
    status_message: StatusMessageSerializer = field()

class SubmitSubscriptionsResponseSerializer(RegistrySerializer):
    subscription_status: Iterable[SubscriptionStatusSerializer] = field()

class QuerySubscriptionRequestSerializer(RegistrySerializer):
    organisation: ReferenceSerializer = field()

class QuerySubscriptionResponseSerializer(RegistrySerializer):
    status_message: StatusMessageSerializer = field()
    subscription: Iterable[SubscriptionSerializer] = field()

class StructuralEventSerializer(RegistrySerializer):
    structures: StructuresSerializer = field(namespace_key='structure')

# # class RegistrationEvent(RegistrySerializer):
#     registration: Registration = field(namespace_key='registry')

class NotifyRegistryEventSerializer(RegistrySerializer):
    event_time: datetime = field()
    object_urn: str = field(localname='ObjectURN')
    registration_id: str = field(localname='RegistrationID')
    subscription_urn: str = field(localname='SubscriptionURN')
    event_action: str = field()
    structural_event: StructuralEventSerializer = field()
    # registration_event: RegistrationEvent = field()

class RegistryInterfaceSubmitStructureRequestSerializer(BaseSDMXMessageSerializer):
    submit_structure_request: SubmitStructureRequestSerializer = field(forward_accesor='submitstructurerequest')

    def to_response(self):
        return RegistryInterfaceSubmitStructureResponseSerializer(
            header=self.header.to_response(),
            submit_structure_response=self.submit_structure_request.to_response()
        )

class RegistryInterfaceSubmitStructureResponseSerializer(BaseSDMXMessageSerializer):
    submit_structure_response: SubmitStructureResponseSerializer = field()

class QueryableDataSourceSerializer(RegistrySerializer):
    data_url: str = field(localname='DataURL', namespace_key='common')
    wsdlurl: str = field(localname='WSDLURL', namespace_key='common')
    wadlurl: str = field(localname='WADLURL', namespace_key='common')
    is_rest_datasource: bool = field(localname='isRESTDatasource', is_attribute=True)
    is_web_service_datasource: bool = field(is_attribute=True)
    tipe: str = field(localname='TYPE', is_attribute=True, default='QUERY')
    tipe: str = field(localname='TYPE', is_attribute=True, default='QUERY')

class DatasourceSerializer(RegistrySerializer):
    simple_data_source: str = field()
    queryable_data_source: QueryableDataSourceSerializer = field()

class RegistrationSerializer(RegistrySerializer):
    provision_agreement: ReferenceSerializer = field()
    datasource: DatasourceSerializer = field()
    reg_id: str = field(localname='id', is_attribute=True)
    valid_from: datetime  = field(is_attribute=True)
    valid_to: datetime  = field(is_attribute=True)
    last_updated: datetime  = field(is_attribute=True)
    index_time_series: bool = field(is_attribute=True, default=False)
    index_data_set: bool = field(is_attribute=True, default=False)
    index_attributes: bool = field(is_attribute=True, default=False)
    index_reporting_period: bool = field(is_attribute=True, default=False)

class RegistrationRequestSerializer(Serializer):
    registration: RegistrationSerializer = field()
    action: str = field(is_attribute=True)

    class Meta:
        app_name ='registry'
        model_name = 'submitstructurerequest'
        namespace_key = 'registry'

class SubmitRegistrationsRequestSerializer(RegistrySerializer):
    registration_request: Iterable[RegistrationRequestSerializer] = field()

    def process_premake(self):
        return self._wrapper.m_header 

    def to_response(self):
        return SubmitRegistrationsResponseSerializer(
            registration_status = self._context.generate_result()
        )

class RegistryInterfaceSubmitRegistrationsRequestSerializer(BaseSDMXMessageSerializer):
    submit_registrations_request: SubmitRegistrationsRequestSerializer = field()

    def to_response(self):
        return RegistryInterfaceSubmitRegistrationsResponseSerializer(
            header=self.header.to_response(),
            submit_structure_response=self.submit_registrations_request.to_response()
        )

class RegistrationStatusSerializer(RegistrySerializer):
    registration: RegistrationSerializer = field()
    status_message: StatusMessageSerializer = field()

class SubmitRegistrationsResponseSerializer(RegistrySerializer):
    registration_status: Iterable[RegistrationStatusSerializer] = field()

class RegistryInterfaceSubmitRegistrationsResponseSerializer(BaseSDMXMessageSerializer):
    submit_registrations_response: SubmitRegistrationsResponseSerializer = field()

class RegistryInterface(BaseSDMXMessageSerializer):

    submit_registrations_request: SubmitRegistrationsRequestSerializer = field() 
    submit_registrations_response: SubmitRegistrationsResponseSerializer = field()
    # query_registration_request: QueryRegistrationRequestSerializer = field()
    # query_registration_response: QueryRegistrationResponseSerializer = field()
    submit_structure_request: SubmitStructureRequestSerializer = field()
    submit_structure_response: SubmitStructureResponseSerializer = field()
    submit_subscriptions_request: SubmitSubscriptionsRequestSerializer = field()
    submit_subscriptions_response: SubmitSubscriptionsResponseSerializer = field()
    query_subscription_request: QuerySubscriptionRequestSerializer = field()
    query_subscription_response: QuerySubscriptionResponseSerializer = field()
    notify_registry_event: NotifyRegistryEventSerializer = field()
