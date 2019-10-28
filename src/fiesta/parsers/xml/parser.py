# parser.py

import inspect

from importlib import import_module
from lxml import etree # TODO work on xml security
from rest_framework.exceptions import ParseError, UnsupportedMediaType
from rest_framework.parsers import BaseParser
from typing import Iterable
from zipfile import ZipFile, is_zipfile

from ...settings import api_settings
from ...utils.coders import decode 
from ...core import constants
from ...core.exceptions import NotImplementedError, ParseSerializeError
from ...core.schema import Schema21

class BaseXMLParser(BaseParser):
    """
    XML parser.
    """
    media_type = 'application/xml'

    def __init__(self, *args, **kwargs):
        self.serializers = import_module(api_settings.DEFAULT_SERIALIZER_MODULE)
    
    def get_version(self, media_type):
        try:
            version = media_type.split(';')[1].split('=')[1]
        except (IndexError, AttributeError):
            version = '2.1'
        if version != '2.1':
            raise UnsupportedMediaType(media_type)
        return version.replace('.', '')

    def get_root(self, stream):
        if is_zipfile(stream):
            temp = stream 
            with ZipFile(temp, mode='r') as zf:
                info = zf.infolist()[0]
                stream= zf.open(info)
        else:
            # undo side effect of is_zipfile
            stream.seek(0)
        try:
            tree = etree.parse(stream)
        except (etree.ParseError, ValueError) as exc:
            raise ParseError(detail=f'XML parse error - {exc}')
        return tree.getroot()

    def validate_roottag(self):
        """Check that roottag is proper given version

        Redefine in subclasses"""
        pass


    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as XML and returns the resulting data.
        """
        self.version = self.get_version(media_type)
        self.root = self.get_root(stream)
        self.validate_roottag()


    def get_serializer_class(self):
        """
        Returns an appropriate serializer class

        Redefine in subclasses"""


    def populate_serializer(self, serializer, complain):
        """
        Convert element to serializer

        Any field values passed during serializer instantiation as keyword arguments are
        overwritten.
        Redefine in subclasses
        """

        if not serializer._elem: serializer._elem = self.root 
        qname = etree.QName(serializer._elem.tag)
        # First check that the element local name is the same as the Dataclass
        # model_name (case insensitive). 
        if complain:
            if not serializer._meta.object_name.startswith(qname.localname):
                raise TypeError(
                    f'{qname} element can not be represented with a {serializer._meta.object_name}'
                )

    def serialize_many_elements(self, serializer, field_meta):
        item_type = field_meta.fld.type.__args__[0]
        for child_element in serializer._elem.itefind(field_meta.tag):
            child_serializer = item_type()
            child_serializer._elem = child_element
            self.populate_serializer(child_serializer, False)
            yield child_serializer

    def parse_structures(self, stream):
        self.root = etree.parse(stream).getroot()
        serializer = self.serializers.StructuresSerializer()
        self.populate_serializer(serializer, False)
        return serializer

class XMLParser21(BaseXMLParser):

    media_type = 'application/xml;version=2.1'

    def parse(self, stream, media_type=None, parser_context=None):
        super().parse(stream, media_type, parser_context)
        schema = Schema21(self.root).schema
        if not schema(self.root):
            errors = [(error.line, error.domain, error.type, error.message) for error in schema.error_log]
            raise ParseError(errors)
        serializer = self.get_serializer_class()()
        self.populate_serializer(serializer, True)
        return serializer

    def get_serializer_class(self):
        payload_tag = etree.QName(self.root[1].tag).localname
        if payload_tag == 'SubmitStructureRequest':
            return self.serializers.RegistryInterfaceSubmitStructureRequestSerializer
        elif payload_tag == 'SubmitRegistrationsRequest':
            return self.serializers.RegistryInterfaceSubmitRegistrationsRequestSerializer
        elif payload_tag == 'Structures':
            return self.serializers.StructureSerializer
        else:
            return NotImplementedError('Parsing a {payload_tag} payload not yet implemented') 

    def validate_roottag(self, root):
        """Check that roottag is proper given version
        """
        roottag = etree.QName(root.tag)
        if roottag.namespace != constants.NAMESPACE_MAP['message']:
            raise ParseError(detail='Invalid root tag: {roottag.text}')
        if roottag.localname not in constants.SDMX_XML21_MESSAGES:
            raise ParseError(detail='Invalid root tag localname: {roottag.localname}')
        if roottag.localname not in constants.IMPLEMENTED_SDMX21_MESSAGES:
            raise NotImplementedError(detail='Parsing SDMX-ML {roottag.localname} not implemented')

    def populate_serializer(self, serializer, complain):
        """
        Convert element to serializer

        Any field values passed during serializer instantiation as keyword arguments are
        overwritten.
        """
        super().populate_serializer(serializer, complain)

        # Iterate through dataclass fields
        for f in serializer._meta.fields: 
            value = None
            field_meta = f.metadata['fiesta']
            tag = field_meta.tag
            if field_meta.is_text:
                value = decode(serializer._elem.text, f.type)
            elif field_meta.is_attribute:
                value = decode(serializer._elem.attrib.get(tag), f.type)
                if not value: value = f.default
            elif inspect.isclass(f.type):
                if issubclass(f.type, self.serializers.Serializer):
                    child_element = serializer._elem.find(tag)
                    if etree.iselement(child_element):
                        child_serializer = f.type()
                        child_serializer._elem = child_element
                        self.populate_serializer(child_serializer, False)
                        value = child_serializer
                # Must be a simple element
                else: 
                    try:
                        value = serializer._elem.find(tag).text
                    except AttributeError:
                        pass
            elif type(f.type) == type(Iterable):
                value = self.serialize_many_elements(serializer, field_meta)
            else:
                raise ParseSerializeError(f'Encountered an unknown type field: {f.type}')
            setattr(serializer, f.name, value)

class  XMLParser(XMLParser21):
    media_type = 'application/xml;version=2.1'
