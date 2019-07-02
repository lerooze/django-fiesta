from dataclasses import fields, field, Field
from pydantic.dataclasses import dataclass
from django.utils.functional import cached_property
from django.apps import apps
from django.db.models.options import make_immutable_fields_list
from django.db import models
from typing import Tuple, List
from inflection import camelize
from lxml.etree import QName
from collections import defaultdict
from rest_framework.request import Request
from fiesta.settings import api_settings 
from fiesta.core import constants
from ..constants import NAMESPACE_MAP, CLASS2RESOURCES
from django.db.models import Q
from inflection import underscore


@dataclass
class ClassOptions: 
    """
    Class to store metadata for a Fiesta Dataclass.

    It is itself a dataclass.

    Parameter Fields
    ---------------
    app_name
        The name of the django app, if any, that the dataclass is associated with.
    model_name
        The model name, if any, that the dataclass stores its fields.
    namespace_key: str
        The namespace_key of the related element
    children_names: Tuple[str]
        Names of Maintainable dataclasses that are its children as defined in the SDMX model

    Attribute Fields
    ----------------
    cls
        The dataclass of the metadata.  It is set in
        `contribute_to_class`.
    object_name: str
        The name of the dataclass.  It is set in `contribute_to_class`.
    model: a Django model class
        The django model object the dataclass uses to store its fields.  It is
        set in `contribute_to_class`.
    fields: tuple of `Field`
        The fields of the dataclass
    resources: tuple of string
        For a maintanable dataclass the resources that full detail of the
        artefact will be rendered in case detail keyword request argument is
        equal to referencestubs
    attr_fields: tuple of Fields
        The fields that are attributes of the related element
    stub_attr_fields: tuple of Fields
        The fields that are attribute stubs of the related element
    nsmap: dict
        The nsmap needed to generate the lxml element
    tag: QName
        The tag of the related element
    children: Tuple[Dataclass]
        Maintainable dataclasses that are its children as defined in the SDMX model
    parents: Tuple[Dataclass]
        Maintainable dataclasses that are its parents
    maintainable:
        The database object of the latest processed Maintainable Artefact
    underscore_name:
        Underscore converted model name

    """
    app_name: str = ''
    model_name: str = ''
    namespace_key: str = ''
    children_names: Tuple[str] = field(default_factory=list)
    structures_field_name: str = field()
    dataclass: object = field(init=False)
    object_name: str = field(init=False)
    model: models.Model = field(init=False)
    fields: Tuple(Field) = field(init=False)
    resources: Tuple(str) = field(init=False)
    attr_fields: Tuple(Field) = field(init=False)
    stub_attr_fields: Tuple(Field) = field(init=False)
    nsmap: dict = field(init=False)
    tag: QName = field(init=False)
    non_attr_fields: Tuple(Field) = field(init=False)
    children: Tuple[object] = field(init=False)
    parents: List[object] = field(init=False)
    maintainable: object = field(init=False)
    underscore_name: str = field(init=False)

    def contribute_to_class(self, cls, name):
        cls._meta = self

        # Post initializations of not initialized fields
        self.cls = cls
        self.object_name = cls.__name__
        self.model = self.get_model()
        self.fields = fields(cls)
        self.resources = self.get_resources
        self.attr_field = self.get_attr_field()
        self.nsmap = self.get_nsmap()
        self.tag = self.get_tag()
        self.non_attr_fields = self.get_non_attr_fields()
        self.children = self.get_children()
        self.set_parents()
        self.underscore_name = underscore(self.object_name)
    
        # Store option values that are derived from other options if not provided

        # new_meta = cls.add_initial_settings(meta, Meta())
        # new_meta.fields = cls.get_fields()
        # new_meta.ns_fields = cls.get_ns_fields(new_meta)
        # new_meta.element_fields = cls.get_element_fields(new_meta)
        # new_meta.attribute_fields = cls.get_attribute_fields(new_meta)
        # new_meta.text_field = cls.get_text_field(new_meta)
        # new_meta.class_name = cls.__name__
        # new_meta.class_wrapper = CLASS2WRAPPER.get(new_meta.class_name)
        # new_meta.model = cls.get_model(new_meta)
        # new_meta.container_name = cls.get_container_name(new_meta)
        # cls.set_parents(new_meta.children)
        # cls._meta = new_meta

    def get_children(self):
        if isinstance(self.children_names, str):
            self.children_names = [self.children_names]
        return tuple(getattr(api_settings.DEFAULT_DATACLASS_MODULE, child_name)
                     for child_name in self.children_names)
    
    def select_child(self, field_name):
        for child in self.children:
            if underscore(child._meta.object_name).startswith(field_name):
                return child


    def set_parents(self):
        for child in self.children:
            child._meta.parents.append(self.cls)

    def get_resources(self):
        return CLASS2RESOURCES.get(self.object_name)  

    def get_model(self):
        if not self.model_name: return
        return apps.get_model(self.app_name, self.model_name)

    def get_attr_fields(self):
        return tuple(f for f in self.fields if f.metadata['fiesta'].is_attribute)

    def get_stub_attr_fields(self):
        stub_keys = ['id', 'agencyID', 'version']
        return  tuple(f for f in self.attr_fields if
                      f.metadata['fiesta'].localname in stub_keys)

    def get_nsmap(self):
        nsmap = {}
        if self.namespace_key:
            nsmap[self.namespace_key] = NAMESPACE_MAP[self.namespace_key]
        for f in self.fields:
            nsmap[f.namespace_key] = NAMESPACE_MAP[f.namespace_key]
        return nsmap

    def get_tag(self):
        if not self.namespace_key: return
        localname = self.object_name.rsplit('Dataclass')[0]
        return QName(NAMESPACE_MAP[self.namespace_key], localname)

    def get_non_attr_fields(self):
        return tuple(f for f in self.fields if f not in self.attr_fields)


    # def _get_fields_and_update_field_meta(self):
    #     """
    #     Returns the fields of the class and updates metadata.
    #
    #     Extended Summary
    #     ----------------
    #     Private API that serves two purposes:
    #         1. Returns the fields of the dataclass
    #         2. Sets defaults on `namespace_key`, `localname` on each field
    #            metadata
    #             
    #     Returns 
    #     -------
    #     tuple
    #         The fields of the class
    #     """
    #     fields = []
    #     for f in fields(self.dataclass):
    #         meta = f.metadata['fiesta']
    #         meta.dataclass = self.dataclass
    #         if not meta.namespace_key: meta.namespace_key = self.namespace_key 
    #         if not meta.localname: meta.localname = self.get_localname(f)
    #         fields.append(f)
    #     return tuple(fields) 

    def get_localname(self, field):
        from fiesta.core.dataclasses import AttributeDataclass
        if issubclass(self.dataclass, AttributeDataclass):
            return camelize(field.name, False)
        return camelize(field.name)


    @cached_property
    def fields_map(self):
        return {f.name: f for f in self.fields}

    @cached_property
    def text_field(self):
        """
        Returns the last defined field if is_text argument is set.

        Used on serializing an element when an element has no children.
        """
        f = self.fields[-1]
        if f.metadata.FIESTA.is_text: return f

    @cached_property
    def children_fields(self):
        return make_immutable_fields_list(
            'children_fields',
            (f for f in self.fields if not f.metadata.FIESTA.is_attribute and
             not f.metadata.FIESTA.is_text)
        ) 

    # def set_parents(cls, children):
    #     for child_cls in children:
    #         child_cls._meta.parent.append(cls)
    #
    # def get_container_name(cls, meta):
    #     if meta.container_name: return meta.container_name
    #     return f"{meta.class_name.split('Dataclass')[0].lower()}s"
    #
    #
    #
    # def get_fields(cls):
    #     return {f.name: f for f in fields(cls)}
    #
    # def get_ns_fields(cls, clsmeta):
    #     # Returns a mapping of namespace => is_attribute => is_text =>
    #     # localname => field 
    #     # localname is either the local element name or the local attribute
    #     # name
    #     
    #     r = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    #     for f in fields(cls):
    #         if f.name == 'extra_attribs': continue
    #         meta = f.metadata['FIESTA']
    #
    #         localname = meta.localname
    #         if not localname: 
    #             upper = False if meta.is_attribute else True 
    #             localname = camelize(f.name, upper)
    #         namespace_key = meta.namespace_key
    #         if not meta.is_attribute and not namespace_key:
    #             namespace_key = clsmeta.namespace_key
    #         namespace = constants.NAMESPACE[namespace_key]
    #         r[namespace][meta.is_attribute][meta.is_text][localname] = f
    #     return r
    #
    # @staticmethod
    # def get_element_fields(clsmeta):
    #     for namespace, nsvalue in clsmeta.ns_fields.items():
    #         for localname, f in nsvalue[False][False].items():
    #             yield (f, QName(namespace, localname))
    #
    # @staticmethod
    # def get_attribute_fields(clsmeta):
    #     for namespace, nsvalue in clsmeta.ns_fields.items():
    #         for localname, f in nsvalue[True][False].items():
    #             yield (f, QName(namespace, localname))
    #
    # @staticmethod
    # def get_text_field(clsmeta):
    #     ns = constants.NAMESPACE[clsmeta.namespace_key]
    #     text_dict = clsmeta.ns_fields[ns][False][True]
    #     if not text_dict: return
    #     for key, f in text_dict.items():
    #         return f

@dataclass
class FieldOptions:
    """
    Dataclass to store metadata to a fiesta field.

    Parameter Fields
    ----------------
    is_text: bool
        Indicates that the field is the text property of the related xml element.
    is_attribute: bool
        Indicates whether the field is an attribute of the related xml element.
    localname: str
        The localname of the xml element/attribute that this field is
        associated with.  It is defaulted to the name of the field camelized.
        If it is an element the first letter is capitalized.  It is not
        relevant if the `is_text` property is set.  The default is set on
        `contribute_to_field_metadata`.
    namespace_key: str
        The namespace_key of the related element.  The default is the
        namespace_key of the class and is set on
        `contribute_to_field_metadata`.
    forward: bool
        Set to indicate a forward relationship field
    forward_accesor: str
        The forward accesor to use to get the field value when provided with a
        related model object.  It is applicable when `forward` is set.

    Attribute Fields
    ----------------
    field: Field
        The Field instance that this metadata instance describes.
    cls: object
        The dataclass in which the field is defined.
    tag: QName
        The qname of the xml element that the field describes.


    """
    is_text: bool = False
    is_attribute: bool = False
    localname: str = None
    namespace_key: str = None
    # related_name: str = None
    forward: bool = False
    forward_accesor: str = None
    field: Field = field(init=False)
    cls: type = field(init=False)
    tag: QName = field(init=False)
    # get_fields of the dataclass options updates this
    # dataclass: object = field(init=False)

    def _post_class_meta_defaults(self, cls):
        from .base import BaseFiestaDataclass 
        # Set dataclass option
        self.cls = cls

        # Set default localname
        if not self.localname:
            if issubclass(self.field.type, BaseFiestaDataclass):
                is_upper = True
            else:
                is_upper = False
            self.localname = camelize(self.field.name, is_upper)

        # Set default namespace_key for not attribute fields
        if self.namespace_key is None and not self.is_attribute:
            self.namespace_key = cls._meta.namespace_key

        # Set tag
        self.tag = QName(NAMESPACE_MAP.get(self.namespace_key), self.localname)

        # Set default forward_accesor
        if self.forward and not self.forward_accesor:
            self.forward_accesor = self.field.name

def default_results():
    # Returns a submitted structures mapping: 
    # package => class => agency => object => version => Submission
    return defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict()))))

@dataclass
class ProcessContextOptions:
    """
    Used to store process context data.

    Parameter Fields
    ----------------
    request: Request
        The request that is the cause of the process loop.
    log: An acquisition log object
        The acquisition log model object related to this submission.
    
    Attribute Fields
    results: 
        Mapping of package => class => agency => object => version =>
        Submission
    result:
        The current result object
    action: str
        The default action to take on processing the artefacts
    external_dependencies: str
        The default external_dependencies when processing the artefacts

    ----------------
    """
    request: Request
    acquisition_obj: object 
    results: defaultdict = field(init=False, default_factory=default_results)
    result: object = field(init=False)
    action: str = field(init=False)
    external_dependencies: bool = field(init=False)
    
    def get_or_add_result(self, submitted_structure):
        r = self.results
        ref = submitted_structure.maintainable_object.dref
        try:
            return r[ref.package][ref.cls][ref.agency_id][ref.object_id][ref.version]
        except KeyError:
            r[ref.package][ref.cls][ref.agency][
                ref.object_id][ref.version] = submitted_structure
        return submitted_structure

    def generate_result(self):
        for package, vp in self.results.items():
            for cls, vc in vp.items():
                for agency, va in vc.items():
                    for object_id, vo in va.items():
                        for version, result in vo.items():
                            yield result 

@dataclass
class RESTfulQueryContextOptions:
    """
    Used to store query options and metadata.

    Parameter Fields
    ----------------
    query: object
        A RESTfulQuery database model object.
    
    Attribute Fields
    ----------------
    structrures_field_names: Tuple[Field]
        A subset of StructuresDataclass fields for the given resource.
    queries: defaultdict(list)
        A map to store Q objects per queried maintainable structure.
    maintainable_field_names: Tuple[str]
        The maintainable artefact field names associated with the resource 
    """
    query: object
    structrures_fields: Tuple[Field] = field(init=True)
    queries_args: defaultdict = field(init=False, default_factory=lambda:
                                      defaultdict(Q))
    maintainable_query_field_names = Tuple[str] = field(init=True)

    def __post_init__(self):
        self.structrures_fields = self.get_structures_fields()
        self.maintainable_field_names = self.get_maintainable_field_names()

    def get_maintainable_query_field_names(self):
        return constants.RESOURCE2MAINTAINABLE(self.query_resource)

    def get_structures_field_names(self):
        if self.query.resource == 'organisationscheme':
            return 'organisation_schemes',
        if self.query.resource == 'agencyscheme':
            return 'organisation_schemes',
        if self.query.resource == 'dataproviderscheme':
            return 'organisation_schemes',
        if self.query.resource == 'dataconsumerscheme':
            return 'organisation_schemes',
        if self.query.resource == 'OrganisationSchemes':
            return 'organisation_schemes',
        if self.query.resource == 'structure':
            return 'organisation_schemes',

    @cached_property
    def all_structures(self):
        return tuple(key._meta.structures_field_name for key in self.queries_kwargs)

RESOURCE2STRUCTURE = {
    'organisationscheme': 'OrganisationSchemes',
    'agencyscheme': 'OrganisationSchemes',
    'dataproviderscheme': 'OrganisationSchemes',
    'dataconsumerscheme': 'OrganisationSchemes',
    'organisationunitscheme': 'OrganisationSchemes',
    'structure': ['OrganisationSchemes']
}

