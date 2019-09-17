# base.py

import inspect
import modeltranslation

from dataclasses import dataclass, fields, InitVar, field
from django.conf import settings
from django.db import models
from lxml import etree
from types import MappingProxyType
from typing import Iterable

from ...utils import inspect as fiesta_inspect
from ...utils.coders import decode, encode

from .options import ClassOptions, FieldOptions

def has_contribute_to_class(value):
    # Only call contribute_to_class() if it's bound.
    return not inspect.isclass(value) and hasattr(value, 'contribute_to_class')

def metafield(func):
    """
    Decorate field to accept FieldOptions arguments as keyword arguments.

    Pass FieldOptions arguments as keyword arguments and populate field
    metadata `fiesta`: `FiestaOptions` pair.
    """
    def wrapper(*args, **kwargs):
        kwargs.setdefault('default', None)
        meta_kwargs = {
            f.name: kwargs.pop(f.name) for 
            f in fields(FieldOptions)
            if f.name in kwargs
        }
        f = func(*args, **kwargs)
        meta = FieldOptions(**meta_kwargs)
        meta.fld = f
        mapping = dict(fiesta=meta)
        setattr(f, 'metadata', MappingProxyType(mapping))
        return f 
    return wrapper

field = metafield(field)

class BaseMetaSerializer(type):
    """Metaclass for all serializers."""

    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = dataclass(super().__new__(cls, name, bases, attrs, **kwargs))
        attr_meta = attrs.get('Meta')
        meta = attr_meta or getattr(new_class, 'Meta', None)
        if not meta: meta = ClassOptions()
        else:
            args = {key: val for key, val in vars(meta).items() 
                    if not key.startswith('_')}
            meta = ClassOptions(**args)
        new_class.add_to_class('_meta', meta)
        new_class.contribute_to_field_metadata()
        return new_class

    def contribute_to_field_metadata(cls):
        """Transfer defaults to field metadata"""
        for f in cls._meta.fields:
            meta = f.metadata['fiesta']
            meta._post_class_meta_defaults(cls)
            # meta = f.metadata['fiesta']
            # if not meta.localname:
            # f.metadata['fiesta'].get_class_defaults(cls, f)

    def add_to_class(cls, name, value):
        if has_contribute_to_class(value):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

class BaseEmptyMetaSerializer(BaseMetaSerializer):
    """
    Metaclass to describe empty SDMX elements.

    No fields must be defined on the class.  It describes an empty element, ie
    an element with no `attrib`, no children and no `text`
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        if new_class._meta.fields: raise AttributeError('Cannot define fields on this class')
        return new_class

class Serializer(metaclass=BaseMetaSerializer):
    """
    A base Serializer of a SDMX artefact.

    It must be subclassed to represent a specific SDMX artefact.
    A Serializer instance is created by:
        * a django model instance
        * a SDMX etree element
        * key, value pairs of the class fields
    After initialization the `process` method is used for CRUD database operations
    and the `to_element` method to deserialize into a SDMX etree element.

    Parameters
    ---------
    instance_or_element: object
        A django.db.Model or an etree.Element
    complain: bool
        Set it to raise KeyError if wrong type `obj` or `element` is passed.

    Attributes
    ----------
    Meta: class 
        A place to store metadata options for the dataclass.

    Notes
    -----
    Initialization by `instance_or_element` arguments will overide any
    provided field kwargs.
    """

    instance_or_element: InitVar = None
    complain: InitVar = True
    
    def __post_init__(self, instance_or_element, complain):

        # Set on _serialize_element used for debugging 
        self._element = None

        # Set on _serialize_instance used for debugging 
        self._instance = None

        # Construct by element 
        if isinstance(instance_or_element, etree._Element):
            self._serialize_element(instance_or_element, complain)
        # Construct by model_instnce
        elif isinstance(instance_or_element, models.Model): 
            self._serialize_instance(instance_or_element, complain)
        else:
            if instance_or_element:
                raise ValueError("Serializer is instantiated by model instance or element")

    def _serialize_instance(self, instance, complain):
        """
        Private method used by `__post_init__` for initialization.
        """

        self._instance = instance
        
        # Is this the proper class to be used?
        if complain:
            if instance.__class__ != self._meta.model:
                raise TypeError(
                    f'Serialization of {instance} is not possible via {self._meta.object_name}'
                )
        # Loop over fields, extract relevant info from instane and assign values  
        for f in self._meta.fields:
            field_meta = f.metadata['fiesta']
            value = getattr(instance, f.name, None)
            if issubclass(f.type, EmptySerializer) and value:
                value = f.type()
            elif issubclass(f.type, Serializer):
                if value:
                    value = f.type(value, complain=False)
                else:
                    value = f.type(instance, complain=False)
            elif type(f.type) == type(Iterable):
                item_type = f.type.__args__[0]
                if not issubclass(item_type, Serializer):
                    raise TypeError('Got an unexpected iterable type {item_type} while serializing {obj}')
                item_set = self.get_item_set(field_meta.related_name)
                value = self.get_item_set_value(item_set, item_type)
            elif field_meta.forward:
                value = getattr(instance, field_meta.forward_accesor, None)
            else:
                raise KeyError(f'Encountered an unknown type field: {f.type}')
            setattr(self, f.name, value)

    def get_item_set(self, related_name):
        return getattr(self._instance, related_name)

    def get_item_set_value(self, item_set, item_type):
        if not item_set: return
        if isinstance(item_set[0]._meta, modeltranslation.manager.MultilingualManager):
            value = (item_type(item, lang=lang) for item in item_set for lang in settings.LANGUAGES)
        else:
            value = (item_type(item) for item in item_set)
        return value

    def _serialize_element(self, element, complain):
        """
        Private API that __post_init__ calls to serialize a SDMX lxml Element
        object.

        Any field values passed during instantiation as keyword arguments are
        overwritten.
        """

        self._element = element
        qname = etree.QName(element.tag)
        # First check that the element local name is the same as the Dataclass
        # model_name (case insensitive). 
        if complain:
            if not self._meta.object_name.startswith(qname.localname):
                raise TypeError(
                    f'{qname} element can not be represented with a {self._meta.object_name}'
                )
        # Iterate through dataclass fields
        for f in self._meta.fields: 
            value = None
            field_meta = f.metadata['fiesta']
            tag = field_meta.tag
            if field_meta.is_text:
                value = decode(element.text, f.type)
            elif field_meta.is_attribute:
                value = decode(element.attrib.get(tag), f.type)
                if not value: value = f.default
            elif inspect.isclass(f.type):
                if issubclass(f.type, Serializer):
                    child_element = element.find(tag)
                    # if field_meta.localname == 'ConceptIdentity': breakpoint() # BREAKPOINT
                    if etree.iselement(child_element):
                        value = f.type(child_element, complain=False)
                # Must be a simple element
                else: 
                    try:
                        value = element.find(tag).text
                    except AttributeError:
                        pass
            elif type(f.type) == type(Iterable):
                value = self.serialize_many_elements(field_meta)
            else:
                raise KeyError(f'Encountered an unknown type field: {f.type}')
            setattr(self, f.name, value)

    def serialize_many_elements(self, field_meta):
        item_type = field_meta.fld.type.__args__[0]
        return (
            item_type(child_element, complain=False)
            for child_element in self._element.iterfind(field_meta.tag)
        )

    def unroll(self):
        """
        Unroll instance by converting any (nested) iterable field values into
        tuples.
        """
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, Serializer):
                value = value.unroll()
            elif fiesta_inspect.non_string_iterable(value):
                value = [val.unroll() for val in value]
            setattr(self, f.name, value)
        return self

    def to_element(self, field=None, resource=None, detail=None):
        """
        Renders into a lxml Element object.

        Parameters
        ----------
        field: Field
            The field of the dataclass for nested calls.
        resource: str  
            The resource keyword argument if the method is called via SDMX
            RESTful webservice call.
        detail: str 
            The detail keyword argument if the method is called via SDMX
            RESTful webservice call.
        """
        tag = field.metadata['fiesta'].tag if field else self._meta.tag

        # Fast field value lookup
        getval = lambda f: getattr(self, f.name, None)

        # Element detail full or stub
        as_stub = self._to_element_as_stub(self._meta, detail, resource) 

        # Get element attributes and create it
        attrib = self._to_element_attrs(as_stub)
        attrib = {key: value for key, value in attrib.items() if value}
        element = self.make_element(tag, attrib)
        
        # Add children elements
        for f in self._meta.non_attr_fields:
            if f.name != 'name' and as_stub: continue
            value = getval(f)
            if not value: continue
            field_meta = f.metadata['fiesta']
            # If it is a text element set its text
            if field_meta.is_text:
                element.text = encode(getval(f), f.type)
            elif inspect.isclass(f.type):
                if issubclass(f.type, Serializer):
                    child_field = getval(f) 
                    if not child_field: continue
                    element.append(child_field.to_element(f, resource, detail))
                else:
                    child_tag = f.metadata['fiesta'].tag
                    child = etree.Element(child_tag)
                    child.text = encode(getval(f), f.type)
                    element.append(child)
            elif type(f.type) == type(Iterable):
                value = getval(f)
                element.extend(item.to_element(f, resource, detail) 
                               for item in value)
            else:
                raise KeyError(f'Encountered an unknown type field: {f.type} while rendering as an element')
        return element

    def make_element(self, tag, attrib):
        return etree.Element(tag, attrib=attrib, nsmap=self._meta.nsmap)

    def _to_element_as_stub(self, class_meta, detail, resource):
        """Returns True if element should be rendered as stub.

        Will be redifined in MaintainableSerializer
        """
        return False

    def _to_element_attrs(self, as_stub):
        """"""
        getval = lambda f: encode(getattr(self, f.name), f.type)
        attr_fields = ['object_id', 'agency_id', 'version'] if as_stub else self._meta.attr_fields
        attrib = {f.metadata['fiesta'].tag: getval(f) for f in attr_fields}
        if as_stub:
            attrib['isExternalReference'] = encode(True, bool)
            attrib['structureURL'] = self.make_structure_url()
        return attrib

    def process(self, wrapper=None, field=None, context=None):
        """
        Main entry point for CRUD database operations

        It inspects the instance and applies andy CRUD operations required.

        Args:
            wrapper (FiestaDataclass): In a nested call it is the
                Serializer instance of the previous node.
            field(Field): The field that a nested process call is bound to.
            context (ProcessMeta): A ProcessContextOptions dataclass instance that is
                used to pass information between nested calls.

        Returns (Model):
            The created, obtained or updated model instance of the model that
            is linked to the serializer.
        """

        # context=dict(request=request, errors={}, 
        # structure=None, submission_results=None, submitted, stop=False)
        
        # This is the wrapper dataclass.  It is None if the `process` call is
        # the initial not nested call.
        self._wrapper = wrapper

        # This is the Field that is currently processed. It is none
        # if it is the root process
        self._field = field

        # This is a dictionary that is used in the process loop of a message
        self._context = context 

        # This is the current db object created and is used to allow other process 
        # methods to refer to it. It is usually set in the preprocess_isvalid
        # method if an obj is created in this method and the same obj is
        # what process_premake returns
        self._obj = None 
        
        # This is created in ItemDataclasses as a reference to
        # the parent object of an item
        self._parent_obj = None

        # Set for rollback database reference.  It is set in the Header class
        # so than in case of a test message the database rollsback after
        # processing the message so no changes are made
        self._sid = None 

        # Set to True if need to stop process early
        self._stop = False

        # Set to True if generated object from process method should not be saved
        self._skip_save = False

        # Set in MaintainableDataclass to store a reference to the
        # SubmissionResultDataclass instance 
        self._result = None

        # Perform initial validations before the field instances are processed
        # and any db object is made.
        self.process_prevalidate()

        # Check if need to stop process early 
        if self._process_stop(): return

        # Get or create the main db object before field instances are
        # processed.
        self._obj = self.process_premake()

        # Check if need to stop process early 
        if self._process_stop(): return

        # Validate the main obj before moving to process field instances
        self.process_validate(self._obj)

        # Check if process needs to stop early
        if self._process_stop(): return

        # Process field instances 
        for f in self._meta.fields:
            value = getattr(self, f.name, None)
            if not value: 
                child_obj = None
            elif issubclass(f.type, Serializer):
                child_obj = value.process(self, f, self._context)
            elif type(f.type) == type(Iterable):
                item_type = f.type.__args__[0]
                if issubclass(item_type, Serializer):
                    child_obj= tuple(item.process(self, f, self._context)
                                     for item in value)
            else:
                child_obj = value
            m_name = f'm_{f.name}'
            setattr(self, m_name, child_obj)

        # Perform validations if any after field instances are processed
        self.process_postvalidate(self._obj)

        # Check whether to stop process now
        if self._process_stop(): return

        # Make main db object after field instances are processed
        self._obj = self.process_postmake(self._obj)
        # Check whether to stop process now
        if self._process_stop(): return
        if not self._skip_save: self._obj.save()
        return self._obj 

    def process_prevalidate(self):
        """
        Run validations before the relevant model instance is made.

        Should be overridden in subclasses if need to have such validations.
        """
        pass

    def process_premake(self):
        """
        Make the relevant model instance before processing the fields.

        Should be overridden or `super`ed in subclasses if need to make such an
        object. 

        Returns:
            A relevant model instance or None
        """
        if not self._meta.model:
            try:
                return self._wrapper._obj
            except AttributeError:
                pass

    def process_validate(self, obj):
        """
        Run validations after the relevant model instance is made but before
        the fields are processed.

        Should be overridden in subclasses if need to have such validations.
        """
        pass

    def process_postvalidate(self, obj):
        """
        Run validations after the relevant model instance is made and after the 
        fields are processed.

        Should be overridden in subclasses if need to have such validations.
        """
        pass

    def process_postmake(self, obj):
        """
        Makes/modifies the relevant model instance after processing the fields.

        Should be overridden in subclasses if need to make/modify such an
        object at this point. 

        Parameters
        ----------
        obj: 
            A model instance or None

        Returns
        -------
            A relevant model instance or None
        """
        return obj 

    def _process_stop(self):
        """
        Internal API to stop the process call early
        """

        if self._stop: return True

    def __eq__(self, other):
        if type(self) != type(other): return False
        gs = lambda f: getattr(self, f.name)
        go = lambda f: getattr(other, f.name)
        for f in fields(self): 
            self_f, other_f = gs(f.name), go(f.name)
            if type(self_f) != type(other_f):
                return False
            if isinstance(self_f, Iterable):
                for s, o in zip(self_f, other_f):
                    if s != o: return False
            else:
                if self_f != other_f: return False
        return True

    @staticmethod
    def build_filter_kwargs(registration):
        kwargs = {}
        if registration.agency_id != 'all':
            kwargs['agency__object_id'] = registration.agency_id
        if registration.version == 'latest':
            kwargs['latest'] = True
        elif registration.version != 'all':
            kwargs['version'] = registration.version
        return kwargs

    @classmethod
    def get_queryset(cls, registration):
        kwargs = cls.build_filter_kwargs(registration)
        return cls._meta.model.filter(**kwargs)

class EmptySerializer(Serializer, metaclass=BaseEmptyMetaSerializer):
    """
    Class to describe empty SDMX elements.
    """
    pass
