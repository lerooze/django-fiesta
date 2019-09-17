"""
Provides XML parsing support.
"""
from importlib import import_module
from zipfile import ZipFile, is_zipfile

from rest_framework.exceptions import ParseError, UnsupportedMediaType
from rest_framework.parsers import BaseParser
from rest_framework.response import Response
from tempfile import SpooledTemporaryFile
import requests

# TODO work on xml security
from lxml import etree
from ...utils.schema import Schema

class XMLParser(BaseParser):
    """
    XML parser.
    """
    media_type = 'application/xml'

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
            raise ParseError('XML parse error - %s' % exc)
        return tree.getroot()

    def validate_roottag(self):
        if not self.root.tag.endswith('RegistryInterface'):
            raise ParseError('Use a RegistryInterface SDMXML message for a POST submission Request')

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
        root = self.get_root(stream)
        schema = Schema(root).schema
        if schema:
            if not schema(root):
                errors = [(error.line, error.domain, error.type, error.message) for error in schema.error_log]
                raise ParseError(errors)
        serializer = self.get_serializer(root)
        return serializer(root)

    def get_serializer(self, root):
        payload_tag = etree.QName(root[1].tag).localname
        if payload_tag == 'SubmitStructureRequest':
            serializers = import_module('fiesta.core.serializers.structure')
            return serializers.RegistryInterfaceSubmitStructureRequestSerializer
        elif payload_tag == 'SubmitRegistrationsRequest':
            serializers = import_module('fiesta.core.serializers.structure')
            return serializers.RegistryInterfaceSubmitRegistrationsRequestSerializer
        elif payload_tag == 'Structures':
            serializers = import_module('fiesta.core.serializers.structure')
            return serializers.StructureSerializer
        else:
            return ParseError('Parsing a %s payload not implemented yet' % payload_tag) 

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
