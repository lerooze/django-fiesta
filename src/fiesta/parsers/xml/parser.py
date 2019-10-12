# parser.py

import inspect
import requests

from importlib import import_module
from lxml import etree # TODO work on xml security
from rest_framework.exceptions import ParseError, UnsupportedMediaType
from rest_framework.parsers import BaseParser
from rest_framework.response import Response
from tempfile import SpooledTemporaryFile
from typing import Iterable
from zipfile import ZipFile, is_zipfile

from ...settings import api_settings
from ...utils.coders import decode 
from ...core import constants
from ...core.exceptions import NotImplementedError, ParseSerializeError

from .schema import Schema21

class XMLParser(BaseParser):
    """
    XML parser.
    """
    media_type = 'application/xml'

    def __init__(self, *args, **kwargs):
        self.serializers = import_module(api_settings.DEFAULT_SERIALIZER_MODULE)

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
        try:
            version = media_type.split(';')[1].split('=')[1]
        except (IndexError, AttributeError):
            version = '2.1'
        if version != '2.1':
            raise UnsupportedMediaType(media_type)
        self.root = self.get_root(stream)
        self.validate_roottag()


    def get_serializer_class(self):
        """
        Returns an appropriate serializer class

        Redefine in subclasses"""

    def get_stream_from_location(self, location):
        cfg = self.create_configuration(location)
        response = requests.get(location, **cfg) 
        if response.status_code == requests.codes.OK:
            source = SpooledTemporaryFile(max_size=2**24, mode='w+b')
            for c in response.iter_content(chunk_size=1000000):
                source.write(c)
        else:
            source = None
        code = int(response.status_code)
        if 400 <= code <= 499:
            return Response(f'Getting {location} failed', code)
        return source

    def get(self, location):
        try:
            stream = self.get_stream_from_location(location)
        except requests.exceptions.MissingSchema:
            # Load data from local file
            # json files must be opened in text mode, all others in binary as
            # they may be zip files or xml.
            try:
                if location.endswith('.json'):
                    mode_str = 'r'
                else:
                    mode_str = 'rb'
                stream = open(location, mode_str)
            except FileNotFoundError:
                stream = location 
        return self.parse(stream)

    def create_configuration(self, location):
        cfg = dict(stream=True, timeout=30.1)
        cfg = self.extend_cfg(cfg)
        return cfg

    def extend_cfg(self, cfg):
        return cfg

    def populate_serializer(self, serializer, complain):
        """
        Convert element to serializer

        Any field values passed during serializer instantiation as keyword arguments are
        overwritten.
        Redefine in subclasses
        """

        serializer._elem = self.root 
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

class XMLParser21(XMLParser):

    def parse(self, stream, media_type=None, parser_context=None):
        super().parse(stream, media_type, parser_context)
        self.validate_roottag()
        schema = Schema21(self.root).schema
        if not schema(self.root):
            errors = [(error.line, error.domain, error.type, error.message) for error in schema.error_log]
            raise ParseError(errors)
        serializer_class = self.get_serializer_class()
        return self.populate_serializer(serializer_class(), True)

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
