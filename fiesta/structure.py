
from collections import defaultdict
from dataclasses import dataclass, fields, InitVar, is_dataclass, asdict
from datetime import datetime, date, timedelta
from dateutil.parser import parse as datetime_convert
from decimal import Decimal
from distutils.util import strtobool
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from inflection import camelize
from lxml.etree import QName, Element
from typing import Iterable
import isodate

from . import constants
from . import models
from .parsers import XMLParser
from .settings import api_settings
from .utils import patterns
from .utils.datastructures import field, Empty

@dataclass
class SDMXObject:
    _namespace_key = None 


    element: InitVar = None
    dbobj: InitVar = None
    
    def __post_init__(self, element, dbobj):
        self._element = element
        self._dbobj = dbobj 
        self._ns_fields = self.get_ns_fields()
        self._fields = self.get_fields()
        self._element_fields = list(self.get_element_fields())
        self._attribute_fields = list(self.get_attribute_fields())
        self._text_field = self.get_text_field()
        self._model_type = self.get_model_type() 
        self._inner_stop = False
        if element is not None and dbobj:
            raise KeyError('element and dbobj can not be both set')
        if element is not None:
            self.parse_element()
        if dbobj:
            self.parse_dbobj()


    def parse_dbobj(self):
        pass

    def parse_element(self):
        # Parsing element and assign values ot fields

        # Parsing element attributes
        for attrib, attrib_value in self._element.attrib.items():
            qname = QName(attrib)
            try:
                f = self._ns_fields[qname.namespace][True][False][qname.localname]
            except KeyError:
                if getattr(self, 'extra_attribs', None):
                    self.extra_attribs.setdefault(qname.namespace, {})[qname.localname] = attrib_value
            else:
                attrib_value = self._convert(attrib_value, f.type)
                setattr(self, f.name, attrib_value)

        # Parsing element with no children that has text attribute
        # Uses the class attribute _field_name to assign it to a field
        text = self._element.text
        if not len(self._element) and text:
            f = self._text_field
            setattr(self, f.name, self._convert(text, f.type))


        # Parsing element with children
        for f, tag in self._element_fields:
            field_type = f.type
            if not getattr(field_type, '_name', None):
                # Working on not iterable children 
                child_element = self._element.find(tag)
                if child_element is None: continue
                if not is_dataclass(f.type):
                    # Working on not dataclass type children 
                    if f.type == Empty: setattr(self, f.name, True)
                    else:
                        setattr(self, f.name,
                                self._convert(child_element.text, f.type))
                else:
                    # Working on dataclass type childrent
                    setattr(self, f.name,
                            field_type(element=child_element))
            else:
                # Working on iterable elements
                ## Extracting the type (uses __args__ attribute of type of field)
                field_type = field_type.__args__[0]
                if is_dataclass(field_type):
                    value = (
                        eval(QName(child.tag).localname)(element=child) 
                        for child in self._element.iterfind(tag)
                    )
                else:
                    value = (self._convert(child.text, field_type) for child in
                             self._element.iterfind(tag))
                if value: setattr(self, f.name, filter(None, value))

    def process(self, parent_obj=None, field_name=None, process_context=None):
        # process_context=dict(request=request, errors={}, 
        # structure=None, submission_results=None, submitted, stop=False)
        
        # This is the parent db object created from the previous process method if any
        self._parent_obj = parent_obj

        # This is the field name of the field instance that is currently processed
        self._field_name = field_name

        # This is the context of the process that defines transition variables
        # needed for iterative process.  It is a dictionary than contains the
        # request, a list of early errors, the submission db object, the
        # structure db object, the submission_results object, the submitted db object and a
        # stop variable that is set to true if need to stop the current process
        # early
        self._process_context = process_context 

        # This is the current db object created and is used to allow process methods to refer to it
        # It is usually set in the preprocess_isvalid method if an obj is
        # created in this method and the same method is what process_make_obj
        # returns
        self._obj = None 

        # This is used if a new contact is created so that appropriate email is sent
        # self._created = None
        
        # Set for rollback database reference.  It is set in the Header class
        self._sid = None 

        # Perform initial validations before the field instances are processed
        # and any db object is made.
        self.preprocess_isvalid()

        # Check if need to stop process early 
        if self._stop_process(): return

        # Make the main db object of the class before field instances are
        # processed.  If needed other db objects are made and stored in the
        # process_context for further reference
        obj = self.preprocess_make_obj()

        # Validate the main obj that is made before field instances are processed
        self.preprocess_isobjvalid(obj)

        # Check if need to stop process early 
        if self._stop_process(): return

        # Process field instances 
        for f in fields(self):
            key = f.name
            val = getattr(self, f.name)
            if isinstance(val, str): continue
            if not isinstance(val, (Iterable, SDMXObject)): continue
            if isinstance(val, SDMXObject):
                child_obj = val.process(obj, key, self._process_context)
            else:
                item_type = self._fields[key].type.__args__[0]
                if not issubclass(item_type, SDMXObject): 
                    child_obj = list(val)
                else: 
                    child_obj= [
                        item.process(obj, key, self._process_context)
                        for item in val 
                    ]
            m_name = f'm_{key}'
            setattr(self, m_name, child_obj)

        # Perform validations if any after field instances are processed
        self.postprocess_isvalid()

        # Check whether to stop process now
        if self._stop_process(): return

        # Make main db object after field instances are processed
        obj = self.postprocess_make_obj(obj)
        return obj 

    def _extend(self, qname, values, item_type, unroll):
        if not issubclass(item_type, SDMXObject):
            for value in values:
                element = Element(qname.text)
                element.text = self._convert(value, item_type, False)
                yield element
        else:
            for value in values:
                yield value.to_element(qname.text, unroll)

    def unroll(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, Iterable) and type(value) != str:
                values = []
                for v in value:
                    if isinstance(v, SDMXObject): values.append(v.unroll())
                    else: values.append(v)
                setattr(self, f.name, values)
            elif isinstance(value, SDMXObject):
                setattr(self, f.name, value.unroll())
        return self

    def to_element(self, tag=None, unroll=False):
        getval = lambda f: getattr(self, f.name)
        attrs = dict(
            (qname.text, self._convert(getval(f), f.type, False))
             for f, qname in self._attribute_fields
             if not getval(f) is None
        )
        extra_attribs = getattr(self, 'extra_attribs', None)
        if extra_attribs:
            extra = {QName(ns, localname).text: value
                     for ns, ns_val in extra_attribs.items()
                     for localname, value in ns_val.items}
            extra_attribs.extend(extra)
        if not tag:
            tag = QName(constants.NAMESPACE[self._namespace_key],
                                self.__class__.__name__).text
            nsmap = constants.NAMESPACE_CLEAN 
        else:
            nsmap = None
        element = Element(tag, attrib=attrs, nsmap=nsmap)
        if self._text_field:
            f = self._text_field
            element.text = self._convert(getval(f), f.type, False)
        for f, qname in self._element_fields:
            value = getval(f)
            if value is None: continue
            if isinstance(value, Empty):
                element.append(Element(qname.text))
            elif isinstance(value, SDMXObject):
                element.append(value.to_element(qname.text))
            elif isinstance(value, Iterable) and type(value) != str:
                field_type = f.type.__args__[0]
                if unroll: 
                    value = list(value)
                    setattr(self, f.name, value)
                element.extend(self._extend(qname, value, field_type, unroll))
            else:
                new_elem = Element(qname.text)
                new_elem.text = self._convert(value, f.type, False)
                element.append(new_elem)
        return element

    def get_model_type(self):
        model = getattr(models, self.__class__.__name__, None)
        if not model: return
        return ContentType.objects.get_for_model(model)

    def append_error(self, key, **attrs):
        description = api_settings['ERROR_DESCRIPTIONS'][key].text.en
        if attrs:
            description.substitute(**attrs)
        self._process_context.errors.append(description)

    def preprocess_isvalid(self):
        pass

    def preprocess_make_obj(self):
        pass

    def preprocess_isobjvalid(self, obj):
        pass

    def postprocess_isvalid(self):
        pass

    def postprocess_make_obj(self, obj):
        return obj 

    def _stop_process(self):
        if self._inner_stop: return True
        if self._process_context.stop: return True
        try:
            message = self._process_context.submitted.status_message
        except (AttributeError, KeyError):
            return
        else: 
            if not message: return
            if message.status: return True 

    @staticmethod
    def _convert(value, val_type, to_python=True):
        if value is None: return value
        if val_type == bool:
            if to_python:
                return bool(strtobool(value))
            else: 
                value = 'true' if value else 'false'
                return value
        elif val_type == datetime:
            if to_python:
                return datetime_convert(value)
            else:
                return value.strftime('%Y-%m-%dT%H:%M:%S')
        elif val_type == date:
            if to_python:
                return datetime_convert(value)
            else:
                return value.strftime('%Y-%m-%d')
        elif val_type == Decimal:
            if to_python:
                return Decimal(value)
            else:
                return str(value)
        elif val_type == timedelta:
            if to_python:
                return isodate.parse_duration(value).totimedelta(start=datetime.now())
            else: return isodate.duration_isoformat(value)
        elif val_type == int:
            if to_python:
                return int(value)
            else:
                return str(value)
        else:
            if to_python:
                return value
            else:
                return str(value)

    def get_fields(self):
        return {f.name: f for f in fields(self)}

    def get_ns_fields(self):
        # Returns a mapping of namespace => is_attribute => is_text => localname => field 
        # localname is either the local element name or the local attribute name (without the namespace)
        
        r = defaultdict(lambda: defaultdict(lambda: defaultdict(dict))) 
        for f in fields(self):
            if f.name == 'extra_attribs': continue
            meta = f.metadata['SDMX']
            localname = meta.localname
            if not localname: 
                localname = camelize(f.name, False) if meta.is_attribute else camelize(f.name)
            namespace_key = meta.namespace_key
            if not meta.is_attribute and not namespace_key:
                namespace_key = self._namespace_key
            namespace = constants.NAMESPACE[namespace_key]
            r[namespace][meta.is_attribute][meta.is_text][localname] = f
        return r

    def get_element_fields(self):
        for namespace, nsvalue in self._ns_fields.items():
            for localname, f in nsvalue[False][False].items():
                yield (f, QName(namespace, localname))

    def get_attribute_fields(self):
        for namespace, nsvalue in self._ns_fields.items():
            for localname, f in nsvalue[True][False].items():
                yield (f, QName(namespace, localname))

    def get_text_field(self):
        ns = constants.NAMESPACE[self._namespace_key]
        text_dict = self._ns_fields[ns][False][True]
        if not text_dict: return
        for key, f in text_dict.items():
            return f

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

@dataclass
class Common(SDMXObject):
    _namespace_key = 'common'

@dataclass
class Registry(SDMXObject):
    _namespace_key = 'registry'

@dataclass
class BaseMessage(SDMXObject):
    _namespace_key = 'message'

@dataclass
class BaseStructure(SDMXObject):
    _namespace_key = 'structure'

@dataclass
class Text(Common):
    text: str = field(is_text=True)
    lang: str = field(is_attribute=True, namespace_key='xml', default='en')

    @classmethod
    def make_text(cls, model_type, dbobj, text_type=None):
        texts = models.Text.objects.filter(
            content_type__pk=model_type.id, object_id=dbobj)
        if text_type:
            texts = texts.filter(text_type=text_type)
        for text in texts:
            yield cls(text=text.text, lang=text.lang)

    def preprocess_make_obj(self):
        nameable_model = ContentType.objects.get_for_model(self._parent_obj)
        try:
            obj = models.Text.objects.get(lang=self.lang, text=self.text,
                                        text_type=self._field_name,
                                        content_type__pk=nameable_model.id,
                                        object_id=self._parent_obj.id)
        except models.Text.DoesNotExist:
            obj = models.Text.objects.create(lang=self.lang, text=self.text,
                                            text_type=self._field_name,
                                            nameable_object=self._parent_obj)
        return obj

@dataclass
class Name(Text):
    pass

@dataclass
class Description(Text):
    pass

@dataclass
class Department(Text):
    pass

@dataclass
class Role(Text):
    pass

@dataclass
class AnnotationText(Text):
    pass

@dataclass 
class BaseContact(BaseMessage):
    name: Iterable[Text] = field(namespace_key='common')
    department: Iterable[Text] = field()
    role: Iterable[Text] = field()
    telephone: Iterable[str] = field()
    fax: Iterable[str] = field()
    x400: Iterable[str] = field()
    uri: Iterable[str] = field(localname='URI')
    email: Iterable[str] = field()

@dataclass 
class Contact(BaseContact):
    name: Iterable[Text] = field(namespace_key='common')
    department: Iterable[Text] = field()
    role: Iterable[Text] = field()
    telephone: Iterable[str] = field()
    fax: Iterable[str] = field()
    x400: Iterable[str] = field()
    uri: Iterable[str] = field(localname='URI')
    email: Iterable[str] = field()

    def get_text(self, model, contact):
        texts = model.objects.filter(contact=contact)
        for text in texts:
            yield text.value

    @classmethod
    def make_contact(cls, dbobj):
        contacts = models.Contact.objects.filter(organisation=dbobj.organisation)
        for contact in contacts:
            name = Text.make_text(contact._model_type, contact, 'names')
            department = Text.make_text(contact._model_type, contact, 'departments')
            role = Text.make_text(contact._model_type, contact, 'roles')
            telephone = contact.get_text(models.Telephone, contact) 
            fax = contact.get_text(models.Fax, contact) 
            x400 = contact.get_text(models.X400, contact) 
            uri = contact.get_text(models.URI, contact) 
            email = contact.get_text(models.Email, contact) 
            yield cls(
                name=name,
                department=department,
                role=role,
                telephone=telephone,
                fax=fax,
                x400=x400,
                uri=uri,
                email=email
            )
    def preprocess_isvalid(self):
        if not self.email:
            self._submission.update_status_message('Warning', '441')
            self._inner_stop = True

    def preprocess_make_obj(self):
        User = settings.AUTH_USER_MODEL
        if self._inner_stop: return
        username = list(self.email)[0]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            password = keyring.get_password('django_sdmx', 'new_user')
            user = User.objects.create(
                username=username,
                email=username,
                password=password
            )
            self._new_user = True
        else:
            self._new_user = False
        obj, _ = models.Contact.objects.get_or_create(
            user=user,
            organisation=self._parent_obj
        )
        self.load_multi(obj, self.telephone, models.Telephone)
        self.load_multi(obj, self.fax, models.Fax)
        self.load_multi(obj, self.x400, models.X400)
        self.load_multi(obj, self.uri, models.URI)
        return obj
    
    def postprocess_make_obj(self, obj):
        if self._new_user:
            self.send_password_reset_email()
        obj.save()
        return obj

    def load_multi(self, obj, data, model):
        for value in data:
            model.objects.get_or_create(contact=obj, value=value)
            
    def send_password_reset_email(self, obj):
        request = self._process_context.request
        form = PasswordResetForm({'email': obj.email})
        if form.is_valid():
            form.save(
                request= request,
                use_https=True,
                email_template_name='registration/password_reset_email.html')

@dataclass
class HeaderContact(BaseContact):

    def preprocess_isvalid(self):
        # Checking that contact has an email
        if not self.email:
            self.append_error('442', org=self._parent_obj)
        username = self.email[0]

        # Checking that user is registered 
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.append_error('453', email=username)

        # Checking that user is a member of Organisation
        try:
            contact = models.Contact.objects.get(organisation=self.parent,
                                                 user=user)
        except models.Contact.DoesNotExist:
            self.append_error('451', user=username, org=self.parent)
            contact = None
        self._obj = contact 

    def preprocess_make_obj(self):
        self._inner_stop = True
        return self._obj

@dataclass
class Party(BaseMessage):
    name: Iterable[Text] = field(namespace_key='common')
    contact: Iterable[HeaderContact] = field()
    object_id: str = field(is_attribute=True, localname='id')

    def preprocess_isvalid(self):

        # Checking that receiver organisation exists
        try:
            receiver = models.Organisation.objects.get(
                object_id=self.object_id)
        except models.Organisation.DoesNotExist:
            self.append_error('444', org=self.object_id)
            receiver = None
        self.obj = receiver 

    def preprocess_make_obj(self):
        return self.obj

    def wsrest_party(self, registration):
        if isinstance(registration.user, AnonymousUser):
            self.object_id='not_supplied'
            return
        contact = HeaderContact(email=[registration.user.username])
        receiver = registration.user.contact.organisation
        self.object_id = receiver.object_id
        self.contact = [contact]

@dataclass
class Sender(Party):
    timezone: str = field()

    def preprocess_isvalid(self):
        # Checking that user is a member of Organisation
        request = self._process_context.request
        sender = models.Organisation.objects.get(
            object_id=self.object_id)
        try:
            user = models.Contact.objects.get(
                organisation=sender, user=request.user)
        except models.Contact.DoesNotExist:
            self.append_error('451', user=self.request.user,
                                   org=sender)
        else:
            self.sender = sender
            self.user = user

    def preprocess_make_obj(self):
        return self.sender

    def wsrest_sender(self):
        self.object_id = api_settings.SENDER_ID 

@dataclass
class Ref(SDMXObject):
    agency_id: str = field(is_attribute=True, localname='agencyID')
    maintainable_parent_id: str = field(is_attribute=True, localname='maintainableParentID')
    maintainable_parent_version: str = field(is_attribute=True)
    container_id: str = field(is_attribute=True, localname='containerID')
    object_id: str = field(is_attribute=True, localname='id')
    version: str = field(is_attribute=True)
    local: bool = field(is_attribute=True)
    cls: str= field(is_attribute=True, localname='class')
    package: str = field(is_attribute=True)

@dataclass
class Reference(SDMXObject):
    ref: Ref = field()
    urn: str = field(localname='URN')

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
        ref = Ref()
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

@dataclass
class PayloadStructure(Common):
    provision_agreement: Reference = field()
    structure_usage: Reference = field()
    structure: Reference = field()
    structure_id: str = field(is_attribute=True, localname='structureID')
    schema_url: str = field(is_attribute=True, localname='schemaURL')
    namespace: str = field(is_attribute=True)
    dimension_at_observation: str = field(is_attribute=True)
    explicit_measures: str = field(is_attribute=True)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)

@dataclass
class Header(BaseMessage):
    object_id: str = field(localname='ID')
    test: bool = field(default=False)
    prepared: datetime = field()
    sender: Sender = field()
    receiver: Party = field()
    name: Iterable[Text] = field(namespace_key='common')
    structure: Iterable[PayloadStructure] = field()
    data_provider: Reference = field()
    data_set_action: str = field()
    data_set_id: str = field(localname='DataSetID')
    extracted: datetime = field()
    reporting_begin: str = field()
    reporting_end: str = field()
    embargo_date: datetime = field()
    source: str = field()

    def postprocess_isvalid(self):
        if self._process_context.errors:
            self._process_context.stop = True

    def postprocess_make_obj(self, obj):
        super().postprocess_make_obj(obj)
        obj = models.Submission(
            object_id=self.object_id,
            test=self.test,
            prepared=self.prepared,
            sender=self.m_sender,
            receiver=self.m_receiver,
            time_received=datetime.now(),
            time_updated=datetime.now(),
        )
        obj.save()
        obj.sender_contacts.add(*self.sender.m_contact)
        obj.receiver_contacts.add(*self.receiver.m_contact)
        self._process_context.submission = obj
        self._sid = transaction.savepoint()
        return obj

    def to_response(self):
        header = Header(
            object_id=self._process_context.submission.id,
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
        self.sender=Sender().wsrest_sender(),
        self.receiver=Party().wsrest_party(registration),

@dataclass
class Annotation(Common):
    annotation_title: str = field()
    annotation_type: str = field()
    annotation_url: str = field(localname='AnnotationURL')
    annotation_text: Iterable[Text] = field()
    object_id: str = field(is_attribute=True, localname='id')

    def preprocess_make_obj(self):
        obj, _ = models.Annotation.objects.get_or_create(
            object_id=self.object_id,
            annotation_title=self.annotation_title,
            annotation_type=self.annotation_type,
            annotation_url=self.annotation_url,
            annotable_object=self._parent_obj,
        )
        return obj

    @classmethod
    def make_annotation(cls, model_type, dbobj):
        annotations = models.Annotation.objects.filter(
            content_type__pk=model_type.id, obj_id=dbobj)
        for annotation in annotations:
            annotation_text = Text.make_text(annotation._model_type, annotation, 'annotation_text')
            yield cls(
                annotation_title=annotation.annotation_title,
                annotation_type=annotation.annotation_type,
                annotation_url=annotation.annotation_url,
                annotation_text=annotation_text
            )

@dataclass
class Annotable(SDMXObject):
    annotations: Iterable[Annotation] = field(namespace_key='common')

    def parse_dbobj(self):
        super().parse_dbobj()
        self.annotations = Annotation.make_annotation(self._model_type, self._dbobj)

@dataclass
class Identifiable(Annotable):
    _namespace_key = 'structure'
    object_id: str = field(is_attribute=True, localname='id')
    urn: str = field(is_attribute=True, localname='urn')
    uri: str = field(is_attribute=True, localname='uri')

    def make_urn(self):
        pass

    def make_uri(self):
        pass

    def parse_dbobj(self):
        super().parse_dbobj()
        self.object_id = self._dbobj.object_id
        self.urn = self.make_urn() 
        self.uri = self.make_uri()

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not obj.object_id:
            obj.object_id= self.object_id
        return obj

@dataclass
class Nameable(Identifiable):
    name: Iterable[Name] = field(namespace_key='common')
    description: Iterable[Description] = field(namespace_key='common')

    def parse_dbobj(self):
        super().parse_dbobj()
        self.name = Text.make_text(self._model_type, self._dbobj, 'name')
        self.description = Text.make_text(self._model_type, self._dbobj, 'description')

@dataclass
class Versionable(Nameable):
    version: str = field(is_attribute=True, default='1.0')
    valid_from: datetime = field(is_attribute=True)
    valid_to: datetime = field(is_attribute=True)

    def parse_dbobj(self):
        super().parse_dbobj()
        self.version = self._dbobj.version
        self.valid_from = self._dbobj.valid_from
        self.valid_to = self._dbobj.valid_to

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not obj.version:
            obj.version = self.version
        if not obj.valid_from:
            obj.valid_from = self.valid_from
        if not obj.valid_to:
            obj.valid_to = self.valid_to
        return obj

@dataclass
class Maintainable(Versionable):
    agency_id: str = field(is_attribute=True, localname='agencyID')
    is_final: bool = field(is_attribute=True, default=False)
    is_external_reference: bool = field(is_attribute=True, default=False)
    service_url: str = field(localname='serviceURL', is_attribute=True)
    structure_url: str = field(localname='structureURL', is_attribute=True)

    def parse_dbobj(self):
        super().parse_dbobj()
        self.agency_id = self._dbobj.agency.object_id
        self.is_final = self._dbobj.is_final

    def get_external(self):
        location = self.structure_url
        if not location:
            self.update_status_message('Failure', '421' ) 
            return
        message = XMLParser().get(location)
        if not isinstance(message, Structure):
            self.update_status_message('Failure', '422' ) 
            return
        structures = asdict(message.structures)
        try:
            fld = Identifiable.underscore(self.__class__.__name__)
            structure = constants.FLDTOSTRUCT[fld]
            obj = list(structures[structure][fld])[0]
        except (IndexError, KeyError, AttributeError):
            self.update_status_message('Failure', '423' ) 
            return
        if (obj.agency_id, obj.object_id, obj.version) != (self.agency_id,
                                                         self.object_id,
                                                         self.version):
            self.update_status_message('Failure', '424' ) 
            return
        return obj

    def get_maintainable_model(self):
        if self.__class__.__name__  in ['AgencyScheme', 'DataProviderScheme',
                                        'DataConsumerScheme',
                                        'OrganisationUnitScheme']: 
            return models.OrganisationScheme
        return getattr(models, self.__class__.__name__)

    def get_or_create_submission(self):
        results = self._process_context.submission_results
        cls, agency, object_id = self.__class__.__name__, self.agency_id, self.object_id
        package, version = constants.CLASSTOPACKAGE[self.__class__.__name__], self.version
        try:
            submission = results[package][cls][agency][object_id][version]
        except KeyError:
            submission = self.create_submission()
            results[package][cls][agency][object_id][version] = submission
        return submission

    def create_submission(self):
        default = self._process_context.structure
        cls=self.__class__.__name__
        package=constants.CLASSTOPACKAGE[cls]
        r = Ref(
            agency_id=self.agency_id,
            object_id=self.object_id,
            version=self.version,
            cls=cls,
            package=package
        )
        urn = f'urn:sdmx:infomodel.{r.package}.{r.cls}={r.agency_id}:{r.object_id}({r.version})' 
        reference = Reference(ref=r, urn=urn)
        submitted_structure = SubmittedStructure(
            maintainable_object=reference, 
            action=default.action, 
            external_dependencies=default.external_dependencies
        )
        submission_result = SubmissionResult(
            submitted_structure=submitted_structure,
            status_message=StatusMessage()
        )
        return submission_result

    def update_status_message(self, status, code):
        status_message = self._submission.status_message
        status_message.status = status
        message_text = status_message.message_text or [] 
        default_text = api_settings['ERROR_DESCRIPTIONS'][code].text
        text = [Text(lang, text) for lang, text in default_text.items()]
        message_text.append(CommonStatusMessage(text=text, code=code))
        status_message.message_text = message_text

    def preprocess_isvalid(self):
        self._submission = self.get_or_create_submission()
        try:
            self.agency = models.Organisation.objects.get(object_id=self.agency_id)
        except models.Organisation.DoesNotExist:
            self.update_status_message('Failure', '433')
            self._inner_stop = True

    def preprocess_make_obj(self):
        if self.is_external_reference:
            sdmxobj = self.get_external()
            self = sdmxobj
        model = self.get_maintainable_model() 
        obj, _ = model.objects.get_or_create(
            agency=self.agency,
            object_id=self.object_id,
            version=self.version
        )
        self._submitted = models.SubmittedStructure.objects.create(
            structure_submission=self._process_context.structure,
            action = self._submission.submitted_structure.action,
            external_dependencies = self._submission.submitted_structure.external_dependencies,
            maintainable_object=obj
        )
        return obj 

    def preprocess_isobjvalid(self, obj):
        if self._submission.submitted_structure.action in ['Replace', 'Delete']:
            if obj.is_final:
                self.update_status_message('Failure', '411') 
            else:
                obj.delete()
                if self._submission.submitted_structure.action == 'Delete':
                    self.update_status_message('S')

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not obj.is_final:
            obj.is_final = self.is_final
        if not self._submission.status_message.status:
            self._submission.status_message.status = 'Success'
        self._submission.process(process_context=self._process_context)
        models.SubmittedStructure.objects.create(
            structure_submission=self._process_context.structure,
            action=self._submission.submitted_structure.action,
            external_dependencies = self._submission.submitted_structure.external_dependencies,
            status_message=self._submission.m_status_message,
            maintainable_object=obj
        )
        return obj

@dataclass
class ItemScheme(Maintainable):
    is_partial: bool = field(is_attribute=True, default=False)

@dataclass
class BaseItem(Nameable):
    parent: Reference = field()

    @classmethod
    def create_parent_reference(cls, dbobj):
        parent = dbobj.get_parent()
        if parent:
            return Reference(
                ref=Ref(object_id=parent.object_id)
            )

@dataclass
class Item(BaseItem):

    @classmethod
    def make_item(cls, dbobj, wrapper):
        model = getattr(models, cls.__name__)
        for item in model.objects.filter(wrapper=dbobj):
            instance = cls(dbobj=item)
            instance._wrapper = wrapper

    def parse_dbobj(self):
        super().parse_dbobj()
        model = getattr(models, self.__class__.__name__)
        self.parent = model.create_parent_reference(self._dbobj)

    def preprocess_make_obj(self):
        model = getattr(models, self.__class__.__name__)
        if not self.parent:
            obj, _ = model.objects.get_or_create(
                object_id=self.object_id,
                wrapper=self._parent_obj,
            )
        else:
            obj = model(
                object_id=self.object_id,
                wrapper=self._parent_obj,
            )
        return obj

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        model = getattr(models, self.__class__.__name__)
        if not self.parent: return obj
        if obj.get_parent(): return obj
        parent_id = self.parent.dref.object_id
        try:
            parent = model.objects.get(object_id=parent_id,
                                             wrapper=self._parent_obj)
        except model.DoesNotExist:
            self._submission.update_status_message('Warning', '431')
        else:
            obj.save(parent=parent)
        return obj


@dataclass
class ManyToManyItem(BaseItem):

    def parse_dbobj(self):
        super().parse_dbobj()
        self.parent = Organisation.create_parent_reference(self._dbobj)

    def postprocess_make_obj(self, obj):
        obj = super().postprocess_make_obj(obj)
        if not self.parent: return obj
        if obj.parent: return obj
        parent_id = self.parent.dref.object_id
        try:
            parent = Organisation.objects.get(object_id=parent_id)
        except Organisation.DoesNotExist:
            self._submission.update_status_message('Warning', '431')
        else:
            parent.add_child(instance=obj)
        return obj



@dataclass
class Organisation(ManyToManyItem):
    contact: Iterable[Contact] = field()

    @classmethod
    def make_organisation(cls, dbobj, wrapper):
        for organisation in dbobj.organisations:
            instance = cls(dbobj=organisation)
            instance._wrapper = wrapper

    def parse_dbobj(self):
        super().parse_dbobj()
        self.contact = Contact.make_contact(self._dbobj)
    
    def preprocess_make_obj(self):
        obj, _ = Organisation.objects.get_or_create(
            object_id=self.object_id,
        )
        return obj

@dataclass
class Agency(Organisation):
    pass

@dataclass
class DataProvider(Organisation):
    pass

@dataclass
class DataConsumer(Organisation):
    pass

@dataclass
class OrganisationUnit(Organisation):
    pass

@dataclass
class OrganisationScheme(ItemScheme):

    def parse_dbobj(self):
        super().parse_dbobj()
        if self._dbobj.__name__ != 'OrganisationScheme':
            raise TypeError('Can only parse OrganisationScheme dbobjects')
    
@dataclass
class AgencyScheme(OrganisationScheme):
    agency: Iterable[Agency] = field() 

    def parse_dbobj(self):
        super().parse_dbobj()
        self.agency = Organisation.make_organisation(self._dbobj, self)

@dataclass
class DataConsumerScheme(OrganisationScheme):
    data_consumer: Iterable[DataConsumer] = field() 

    def parse_dbobj(self):
        super().parse_dbobj()
        self.data_consumer = Organisation.make_organisation(self._dbobj)

@dataclass
class DataProviderScheme(OrganisationScheme):
    data_provider: Iterable[DataProvider] = field() 

    def parse_dbobj(self):
        super().parse_dbobj()
        self.data_provider = Organisation.make_organisation(self._dbobj)

@dataclass
class OrganisationUnitScheme(OrganisationScheme):
    organisation_unit: Iterable[OrganisationUnit] = field() 

    def parse_dbobj(self):
        super().parse_dbobj()
        self.organisation_unit = Organisation.make_organisation(self._dbobj)

@dataclass
class OrganisationSchemes(BaseStructure):
    agency_scheme: Iterable[AgencyScheme] = field()
    data_consumer_scheme: Iterable[DataConsumerScheme] = field()
    data_provider_scheme: Iterable[DataProviderScheme] = field()
    organisation_unit_scheme: Iterable[OrganisationUnitScheme] = field()

@dataclass
class Code(Item):
    pass

@dataclass
class Codelist(ItemScheme):
    code: Iterable[Code] = field() 

    def parse_dbobj(self):
        super().parse_dbobj()
        self.code = Item.make_item(self._dbobj, self)

@dataclass
class Codelists(BaseStructure):
    codelist: Iterable[Codelist] = field()

@dataclass
class Format(BaseStructure):
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
    

    def parse_dbobj(self):
        super().parse_dbobj()
        for f in self._dbobj._meta.fields():
            setattr(self, f.name, getattr(self._dbobj, f.name))

    def preprocess_make_obj(self):
        obj, _ = models.Format.objects.get_or_create(
            **asdict(self)
        )
        return obj

@dataclass
class Representation(BaseStructure):
    text_format: Format = field()
    enumeration: Reference = field()
    enumeration_format: Format = field()

    def parse_dbobj(self):
        super().parse_dbobj()
        val = self._dbobj.text_format
        if val:
            self.text_format = Format(dbobj=val)
        val = self._dbobj.enumeration
        if val:
            self.enumeration = Reference(
                ref=Ref(
                    agency_id=val.agency.object_id,
                    object_id=val.object_id,
                    version=val.version,
                    cls='Codelist',
                    package='codelist'
                )
            )
        val = self._dbobj.enumeration_format
        if val:
            self.text_format = Format(dbobj=val)
            
    def preprocess_make_obj(self):
        enumeration = self.enumeration
        if enumeration:
            ref = enumeration.dref
            try:
                codelist = models.Codelist.get(
                    agency_id=ref.agency_id,
                    object_id=ref.object_id,
                    version=ref.version
                )
            except models.Codelist.DoesNotExist:
                self._submission.update_status_message('Warning', 432)
                return
        obj, _ = models.Representation.objects.get_or_create(
            text_format=self.m_text_format,
            enumeration=codelist,
            enumeration_format=self.m_enumeration_format)
        return obj

@dataclass
class ISOConceptReference(BaseStructure):
    concept_agency: str = field()
    concept_scheme_id: str = field(localname='ConceptSchemeID')
    concept_id: str = field(localname='ConceptID')

    def preprocess_make_obj(self):
        obj, _ = models.ISOConceptReference.objects.get_or_create(
            asdict(self))
        return obj

@dataclass
class Concept(Item):
    core_representation: Representation = field()
    iso_concept_reference: ISOConceptReference = field(localname='ISOConceptReference')


    def parse_dbobj(self):
        super().parse_dbobj()
        val = self._dbobj.core_representation
        if val:
            self.core_representation = Representation(dbobj=val)
        val = self._dbobj.iso_concept_reference
        if val:
            self.iso_concept_reference = ISOConceptReference(dbobj=val)


    def postprocess_make_obj(self, obj):
        super().postprocess_make_obj(obj)
        if not obj.core_representation:
            obj.core_representation = self.m_core_representation
        if not obj.iso_concept_reference:
            obj.iso_concept_reference = self.m_iso_concept_reference
        obj.save()
        return obj

@dataclass
class ConceptScheme(ItemScheme):
    concept: Iterable[Concept] = field() 

    def parse_dbobj(self):
        super().parse_dbobj()
        self.concept = Item.make_item(self._dbobj, self)

@dataclass
class Concepts(BaseStructure):
    concept_scheme: Iterable[ConceptScheme] = field()

@dataclass
class Structures(BaseStructure):
    organisation_schemes: OrganisationSchemes = field()
    # dataflows: Dataflows = field()
    # metadataflows: Metadataflows = field()
    # category_schemes: CategorySchemes = field()
    # categorisations: Categorisations = field()
    codelists: Codelists = field()
    # hierarchical_codelists: HierarchicalCodelists = field()
    concepts: Concepts = field()
    # metadata_structures: MetadataStructures = field()
    # data_structures: DataStructures = field()
    # structure_sets: StructureSets = field()
    # reporting_taxonomies: ReportingTaxonomies = field()
    # processes: Processes = field()
    # constraints: Constraints = field()
    # provision_agreements: ProvisionAgreements = field()

    def retrieve(self, registration):
        if registration.resource == 'organisationscheme':
            pass

@dataclass
class Message(Common):
    text: Iterable[Text] = field()
    code: str = field(is_attribute=True)
    severity: str = field(is_attribute=True)
    
@dataclass
class Footer(SDMXObject):
    _namespace_key = 'footer'
    message: Iterable[Message] = field()

    def preprocess_isvalid(self):
        errors = (message for message in self.message if message.severity in
                  ['Error', 'Warning'])
        if errors: 
            self.append_error('461', errors=', '.join(errors))
            self._process_context.stop = True

@dataclass
class Structure(BaseMessage):
    header: Header = field()
    structures: Structures = field()
    footer: Footer = field(namespace_key='footer')

    def to_request(self):
        submit_structure_request = SubmitStructureRequest(
            structures=self.structures,
            action='Replace',
            external_dependencies=True
        ) 
        sender = Sender(object_id='ECB')
        receiver = Party(object_id='SDMX')
        header = Header(
            object_id='django_sdmx_001',
            test=False,
            prepared=datetime.now(),
            sender=sender,
            receiver=receiver
        )
        return RegistryInterfaceSubmitStructureRequest(
            header=header,
            submit_structure_request=submit_structure_request
        )

    def retrieve(self, registration):
        self.structures = Structures().retrieve(registration)
        registration.save()
        self.header = Header().to_structure(registration)

@dataclass
class SubmittedStructure(Registry):
    maintainable_object: Reference = field()
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True) 

@dataclass
class SubmitStructureRequest(Registry):
    structure_location: str = field() 
    structures: Structures = field(namespace_key='structure')
    submitted_structure: Iterable[SubmittedStructure] = field()
    action: str = field(is_attribute=True)
    external_dependencies: bool = field(is_attribute=True) 

    def preprocess_isvalid(self):
        if not self.structures:
            loc = self.structure_location
            message = XMLParser().get(loc)
            if not isinstance(message, Structure):
                self._parent_obj.delete()
                self.append_error('425', loc=loc)
                self._process_context.stop = True
            self.structures = message.structures

    def preprocess_make_obj(self):
        obj = models.Structure.objects.create(
            submission=self._process_context.submission,
            structure_location=self.structure_location,
            action=self.action,
            external_dependencies=self.external_dependencies
        )
        self._process_context['structure'] = obj
        self._process_context['submission_results'] = self.initialize_submission_results()
        return obj

    def initialize_submission_results(self):
        # Returns a submitted structures mapping: 
        # package => class => agency => object => version => Submission
        
        results = defaultdict(lambda: defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict()))))
        for submission in self.submitted_structure:
            d = submission.maintainable_object.dref
            results[d.package][d.ref_class][d.agency_id][d.object_id][d.version] = self.to_submission_result(submission) 
        return results 

    def to_submission_result(self, submission):
        ref = submission.maintainable_object.dref
        urn = submission.maintainable_object.make_maintainable_urn()
        reference = Reference(ref=ref, urn=urn)
        submitted_structure = SubmittedStructure(
            maintainable_object=reference, 
            action=submission.action or self.action, 
            external_dependencies=submission.external_dependencies or self.external_dependencies
        )
        submission_result = SubmissionResult(
            submitted_structure=submitted_structure,
            status_message=StatusMessage()
        )
        return submission_result

    def postprocess_isvalid(self):
        submission = self._process_context.submission
        submission.time_updated = datetime.now()
        submission.save()

    def to_response(self):
        return SubmitStructureResponse(
            submission_result = self.submission_results() 
        )

    def submission_results(self):
        for package, vp in self._process_context.submission_results.items():
            for cls, vc in vp.items():
                for agency, va in vc.items():
                    for object_id, vo in va.items():
                        for version, result in vo.items():
                            yield result 

@dataclass
class CommonStatusMessage(Common):
    text: Iterable[Text] = field()
    code: str = field(is_attribute=True)

    def preprocess_make_obj(self):
        obj, _ = models.MessageText.objects.get_or_create(
            code = self.code 
        )
        return obj

@dataclass
class StatusMessage(Registry):
    message_text: Iterable[CommonStatusMessage] = field()
    status: str = field(is_attribute=True)

    def preprocess_make_obj(self):
        obj = models.StatusMessage.objects.create(
            status=self.status
        )
        return obj

    def postprocess_make_obj(self, obj):
        if self.message_text:
            obj.add(*self.m_message_text)
        return obj

@dataclass
class SubmissionResult(Registry):
    submitted_structure: SubmittedStructure = field()
    status_message: StatusMessage = field()

    def update_status_message(self, status, code):
        self.status_message.status = status
        message_text = self.status_message.message_text or [] 
        default_text = api_settings['ERROR_DESCRIPTIONS'][code].text
        text = [Text(lang, text) for lang, text in default_text.items()]
        message_text.append(CommonStatusMessage(text=text, code=code))
        self.status_message.message_text = message_text

@dataclass
class SubmitStructureResponse(Registry):
    submission_result: Iterable[SubmissionResult] = field()

@dataclass
class NotificationURL(Registry):
    notification_url: str = field(is_text=True)
    is_soap: str = field(localname='isSOAP', is_attribute=True)

@dataclass
class ValidityPeriod(Registry):
    start_date: date = field()
    end_date: date = field()

@dataclass
class IdentifiableObjectEvent(Registry):
    all_instances: Empty = field(localname='All', default=False)
    urn: str = field(localname='URN')
    object_id: str = field(localname='ID', default='%')

@dataclass
class VersionableObjectEvent(IdentifiableObjectEvent):
    version: str = field(localname='ID', default='%')

@dataclass
class StructuralRepositoryEvents(Registry):
    agency_id: Iterable[str] = field(localname='AgencyID', default='%')
    all_events: Empty = field(default=False)
    agency_scheme: Iterable[VersionableObjectEvent] = field()
    data_consumer_scheme: Iterable[VersionableObjectEvent] = field()
    data_provider_scheme: Iterable[VersionableObjectEvent] = field()
    organisation_unit_scheme: Iterable[VersionableObjectEvent] = field()
    dataflow: Iterable[VersionableObjectEvent] = field()
    metadataflow: Iterable[VersionableObjectEvent] = field()
    category_scheme: Iterable[VersionableObjectEvent] = field()
    categorisation: Iterable[IdentifiableObjectEvent] = field()
    codelist: Iterable[VersionableObjectEvent] = field()
    hierarchical_codelist: Iterable[VersionableObjectEvent] = field()
    concept_scheme: Iterable[VersionableObjectEvent] = field()
    metadata_structure_definition: Iterable[VersionableObjectEvent] = field()
    key_family: Iterable[VersionableObjectEvent] = field()
    structure_set: Iterable[VersionableObjectEvent] = field()
    reporting_taxonomy: Iterable[VersionableObjectEvent] = field()
    process: Iterable[VersionableObjectEvent] = field()
    attachment_constraint: Iterable[VersionableObjectEvent] = field()
    content_constraint: Iterable[VersionableObjectEvent] = field()
    provision_agreement: Iterable[VersionableObjectEvent] = field()
    event_type: str = field(is_attribute=True, localname='TYPE', default='STRUCTURE')

@dataclass
class EventSelector(Registry):
    structural_repository_events: StructuralRepositoryEvents = field()
    # data_registration_events: DataRegistrationEvents = field()
    # metadata_registration_events: MetadataRegistrationEvents = field()

@dataclass
class Subscription(Registry):
    organisation: Reference = field()
    registry_urn: str = field(localname='RegistryURN')
    notification_mail_to: Iterable[NotificationURL] = field()
    notification_http: Iterable[NotificationURL] = field(localname='NotificationHTTP')
    subscriber_assigned_id: str = field(namespace_key='SubscriberAssignedID')
    validity_period: ValidityPeriod = field()
    event_selector: EventSelector = field() 
    action: str = field(is_attribute=True)

@dataclass
class SubmitSubscriptionsRequest(Registry):
    subscription_request: Iterable[Subscription] = field()

@dataclass
class SubscriptionStatus(Registry):
    subscription_urn: str = field(localname='Subscription_URN')
    subscriber_assigned_id: str = field(localname='SubscriberAssignedID')
    status_message: StatusMessage = field()

@dataclass
class SubmitSubscriptionsResponse(Registry):
    subscription_status: Iterable[SubscriptionStatus] = field()

@dataclass
class QuerySubscriptionRequest(Registry):
    organisation: Reference = field()

@dataclass
class QuerySubscriptionResponse(Registry):
    status_message: StatusMessage = field()
    subscription: Iterable[Subscription] = field()

@dataclass
class StructuralEvent(Registry):
    structures: Structures = field(namespace_key='structure')

# @dataclass
# class RegistrationEvent(Registry):
#     registration: Registration = field()

@dataclass
class NotifyRegistryEvent(Registry):
    event_time: datetime = field()
    object_urn: str = field(localname='ObjectURN')
    registration_id: str = field(localname='RegistrationID')
    subscription_urn: str = field(localname='SubscriptionURN')
    event_action: str = field()
    structural_event: StructuralEvent = field()
    # registration_event: RegistrationEvent = field()

@dataclass
class BaseRegistryInterface(BaseMessage):
    header: Header = field()
    footer: Footer = field(namespace_key='footer')

@dataclass
class RegistryInterfaceSubmitStructureRequest(BaseRegistryInterface):
    submit_structure_request: SubmitStructureRequest = field()

    def to_response(self):
        return RegistryInterfaceSubmitStructureResponse(
            header=self.header.to_response(),
            submit_structure_response=self.submit_structure_request.to_response()
        )

@dataclass
class RegistryInterfaceSubmitStructureResponse(BaseRegistryInterface):
    submit_structure_response: SubmitStructureResponse = field()

@dataclass
class RegistryInterface(BaseRegistryInterface):
    # submit_registrations_request: SubmitRegistrationsRequest = field() 
    # submit_registrations_response: SubmitRegistrationsResponse = field()
    # query_registration_request: QueryRegistrationRequest = field()
    # query_registration_response: QueryRegistrationResponse = field()
    submit_structure_request: SubmitStructureRequest = field()
    submit_structure_response: SubmitStructureResponse = field()
    submit_subscriptions_request: SubmitSubscriptionsRequest = field()
    submit_subscriptions_response: SubmitSubscriptionsResponse = field()
    query_subscription_request: QuerySubscriptionRequest = field()
    query_subscription_response: QuerySubscriptionResponse = field()
    notify_registry_event: NotifyRegistryEvent = field()
