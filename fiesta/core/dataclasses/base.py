
from dataclasses import dataclass, fields, InitVar, field
from types import MappingProxyType
from fiesta.core.dataclasses.options import ClassOptions, FieldOptions
import inspect
from fiesta.utils import inspect as fiesta_inspect
from fiesta.utils.coders import decode, encode
from lxml.etree import QName, Element
from typing import Iterable

def _has_contribute_to_class(value):
    # Only call contribute_to_class() if it's bound.
    return not inspect.isclass(value) and hasattr(value, 'contribute_to_class')

def metafield(func):
    """
    Decorate field to accept FieldOptions arguments as keyworkd arguments.

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
        meta.field = f
        mapping = dict(fiesta=meta)
        setattr(f, 'metadata', MappingProxyType(mapping))
        return f 
    return wrapper

field = metafield(field)

class BaseFiestaDataclass(type):
    """Metaclass for all dataclasses."""

    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__
        attr_meta = attrs.pop('Meta', None)
        new_class = dataclass(super_new(cls, name, bases, attrs, **kwargs))
        meta = attr_meta or getattr(cls, 'Meta', None)
        if not meta: meta = ClassOptions()
        else:
            args = {key: val for key, val in vars(meta) if not
                    key.startswith('_')}
            meta = ClassOptions(**args)
        new_class.add_to_class('_meta', meta)
        new_class.contribute_to_field_metadata()
        return cls

    def contribute_to_field_metadata(cls):
        """Transfer defaults to field metadata"""
        for f in cls._meta.fields:
            meta = f.metadata['fiesta']
            meta._post_class_meta_defaults(cls)
            # meta = f.metadata['fiesta']
            # if not meta.localname:
            # f.metadata['fiesta'].get_class_defaults(cls, f)

    def add_to_class(cls, name, value):
        if _has_contribute_to_class(value):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

class BaseEmptyFiestaDataclass(BaseFiestaDataclass):
    """
    Metaclass to describe empty SDMX elements.

    No fields must be defined on the class.  It describes an empty element, ie
    an element with no `attrib`, no children and no `text`
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super(cls, name, bases, attrs, **kwargs)
        if new_class._meta.fields: raise AttributeError('Cannot define fields on this class')

class FiestaDataclass(metaclass=BaseFiestaDataclass):
    """
    A pythonic representation of any SDMX artefact

    The FiestaDataclass provides a base class which is used to write
    specialized classes to represent specific SDMX artefacts.  Subclasses are
    initialized by:
        * a django model instance
        * an lxml SDMX element
        * key, value pairs of the class fields
    After initialization the `process` method is used for CRUD database operations
    and the `to_element` method to deserialize into a lxml SDMX element.

    Parameters
    ---------
    django_obj: django model object 
        A django model instance used for instantiation
    element: lxml element object
        A lxml element used for instantiation.
    complain: bool
        Set it to raise KeyError if inappropriate `obj` or `element` is passed.

    Attributes
    ----------
    Meta: class 
        A place to store metadata options for the dataclass.

    Notes
    -----
    Initialization by either `obj` or `element` arguments will overide any
    provided field kwargs.
    """

    django_obj: InitVar = None
    element: InitVar = None
    complain: InitVar = True
    
    def __post_init__(self, django_obj, element, complain):
        # Construct cls by obj or element not both
        if element is not None and django_obj:
            raise KeyError('`element` and `django_obj` cannot be both set')

        # Construct by element 
        if element is not None: 
            self._serialize_element(element, complain)
            self.finalize_element_serialization()

        # Construct by django_obj
        if django_obj: 
            self._serialize_object(django_obj, complain)
            self.finalize_object_serialization(django_obj)

        # Set on _serialize_element used for debugging 
        self._element = None

    def _serialize_object(self, django_obj, complain):
        """
        Private method used by `__post_init__` for initialization.
        """
        
        # Is this the proper class to be used?.
        if complain:
            if django_obj.__class__ != self._meta.model:
                raise TypeError(
                    f'Serialization of {django_obj} is not possible via {self._meta.object_name}'
                )
        # Loop over fields, extract relevant info from obj and assign values  
        for f in self._meta.fields:
            field_meta = f.metadata['fiesta']
            value = getattr(django_obj, f.name, None)
            if issubclass(f.type, EmptyDataclass) and value:
                value = f.type()
            elif issubclass(f.type, FiestaDataclass):
                if field_meta.forward: obj = getattr(django_obj, field_meta.forward_accesor) 
                value = f.type(obj, complain=False)
            elif fiesta_inspect.non_string_iterable(f.type):
                item_type = f.type.__args__[0]
                if not issubclass(item_type, FiestaDataclass):
                    raise TypeError('Got an unexpeced iterable type {item_type} while serializing {obj}')
                value = item_type.generate_many(obj, f)
            elif field_meta.forward:
                value = getattr(obj, field_meta.forward_accesor, None)
            setattr(self, f.name, value)

    def finalize_object_serialization(self):
        """
        Pulbic API that can be used to modify the standard serialization of an
        Django model instance.

        It is primarily used to compute the field values that are derived from
        other field values.
        """
        pass

    def _serialize_element(self, element, complain):
        """
        Private API that __post_init__ calls to serialize a SDMX lxml Element
        object.

        Any field values passed during instantiation as keyword arguments are
        overwritten.
        """

        self._element = element
        qname = QName(element.tag)
        # First check that the element local name is the same as the Dataclass
        # model_name (case insensitive). 
        if complain:
            if not self._meta.object_name.startswith(qname.localname):
                raise TypeError(
                    f'{qname} element can not be represented with a {self._meta.object_name}'
                )
        # Iterate through dataclass fields
        for f in self._meta.fields: 
            field_meta = f.metadata['fiesta']
            tag = field_meta.tag
            if field_meta.is_text:
                value = decode(element.text, f.type)
            elif field_meta.is_attribute:
                value = decode(element.attrib.get(tag), f.type)
                if not value: value = f.default
            elif issubclass(f.type, FiestaDataclass):
                child_element = element.find(tag)
                if not child_element is None:
                    value = f.type(element=child_element)
            elif fiesta_inspect.non_string_iterable(f.type):
                item_type = f.type.__args__[0]
                value = (item_type(element=child_element) 
                         for child_element in element.iterfind(tag))
            else: # Must be a simple element
                value = element.find(tag).text
            setattr(self, f.name, value)

    def unroll(self):
        """
        Unroll instance by converting any (nested) iterable field values into
        tuples.
        """
        for f in fields(self):
            value = getattr(self, f.name)
            if fiesta_inspect.non_string_iterable(value):
                value = list(v.unroll() for v in value)
                setattr(self, f.name, tuple(value))
            elif isinstance(value, FiestaDataclass):
                setattr(self, f.name, value.unroll())
        return self

    def _to_element_as_stub(self, class_meta, detail, resource):
        """Returns True if element should be rendered as stub.

        Will be redifined in MaintainableDataclass
        """
        return False

    def _to_element_attrs(self, as_stub):
        """"""
        getval = lambda f: encode(getattr(self, f.name), f.type)
        attr_fields = self._meta.stub_attr_fields if as_stub else self._meta.attr_fields
        attrib = {f.metadata['fiesta'].qname: getval(f) for f in attr_fields}
        if as_stub:
            attrib['isExternalReference'] = encode(True, bool)
            attrib['structureURL'] = self.make_structure_url()
        return attrib

    def to_element(self, field=None, resource=None, detail=None):
        """
        Renders into a lxmx Element object.

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
        tag = field.tag if field else self._meta.tag

        # Fast field value lookup
        getval = lambda f: getattr(self, f.name)

        # Element detail full or stub
        as_stub = self._to_element_as_stub(self._meta, detail, resource) 

        # Get element attributes and create it
        attrib = self._to_element_attrs(as_stub)
        element = Element(tag, attrib=attrib, nsmap=self._meta.nsmap)
        
        # Add children elements
        for f in self._meta.non_attr_fields:
            if f.name != 'name' and as_stub: continue
            field_meta = f.metadata['fiesta']
            # If it is a text element set its text
            if field_meta.is_text:
                element.text = encode(getval(f), f.type)
            elif issubclass(f.type, FiestaDataclass):
                element.append(getval(f).to_element(f, resource, detail))
            elif issubclass(f.type, Iterable):
                element.extend(item.to_element(f, resource, detail) 
                               for item in getval(f))
            else:
                raise KeyError(f'Encountered an unknown type field: {f.type} while rendering as an element')
        return element

    def process(self, wrapper=None, field=None, context=None):
        """
        Main entry point for CRUD operations on the Fiesta SDMX Django database.

        It inspects the instance and perfoms andy CRUD operations required.

        Args:
            wrapper (FiestaDataclass): If a nested process call it is the
                FiestaDataclass instance of the previous node.
            field(Field): The field that a nested process call is bound to.
            context (ProcessMeta): A ProcessContextOptions dataclass instance that is
                used to pass information between nested process calls
                transistions.

        Returns (Model):
            The created, obtained or updated for the database model that this
                class is linked to.
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
        # Its keys are:
        # 'request': The request object
        # 'acquisition_obj': An acquisition object
        # 'submitted_structure_results': A container with submission_results 
        # 'maintainable_obj': A maintainable object database model instance (reseted)
        # 'result': A dataclass that contains the latest SubmissionResult instance (reseted)
        # context.setdefault('submitted_structure_results', self.initialize_results())
        # context.setdefault('maintainable_obj', None)
        # context.setdefault('result', None)
        # if request: context['request'] = request
        # if acquisition_obj: context['acquisition_obj'] = acquisition_obj 
        self._context = context 

        # This is the current db object created and is used to allow other process 
        # methods to refer to it. It is usually set in the preprocess_isvalid
        # method if an obj is created in this method and the same method is
        # what process_premake returns
        self._obj = None 
        
        # This is created in ItemDataclasses as a reference to
        # the parent object of an item
        self._parent_obj = None

        # Set for rollback database reference.  It is set in the Header class
        # and in case of  a test message the database rollsback after
        # processing the message
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

        # Validate the main obj before moving to process field instances
        self.process_validate(self._obj)

        # Check if process needs to stop early
        if self._process_stop(): return

        # Process field instances 
        for f in self._meta.fields:
            value = getattr(self, f.name)
            # field_meta = f.metadata['fiesta']
            # if isinstance(value, str): continue
            # if not isinstance(value, (Iterable, FiestaDataclass)): continue
            if issubclass(f.type, FiestaDataclass):
                child_obj = value.process(self, f, self._context)
            elif fiesta_inspect.non_string_iterable(f.type):
                item_type = f.type.__args__[0]
                if issubclass(item_type, FiestaDataclass):
                    child_obj= ( 
                        item.process(self, f, self._context)
                        for item in value
                    )
                    tuple(child_obj)
            m_name = f'_{f.name}'
            setattr(self, m_name, child_obj)

        # Perform validations if any after field instances are processed
        self.process_postvalidate()

        # Check whether to stop process now
        if self._process_stop(): return

        # Make main db object after field instances are processed
        self._obj = self.process_postmake(self._obj)
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
                return self._meta.wrapper._obj
            except AttributeError:
                pass

    def process_validate(self, obj):
        """
        Run validations after the relevant model instance is made but before
        the fields are processed.

        Should be overridden in subclasses if need to have such validations.
        """
        pass

    def process_postvalidate(self):
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

    def _process_get_or_add_result(self, submitted_structure):
        r = self._context.results
        ref = submitted_structure.maintainable_object.dref
        try:
            return r[ref.package][ref.cls][ref.agency_id][ref.object_id][ref.version]
        except KeyError:
            r[ref.package][ref.cls][ref.agency][
                ref.object_id][ref.version] = submitted_structure
        return submitted_structure


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

class EmptyDataclass(FiestaDataclass, metaclass=BaseEmptyFiestaDataclass):
    """
    Class to describe empty SDMX elements.
    """
    pass
