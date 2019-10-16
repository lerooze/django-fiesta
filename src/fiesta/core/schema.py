import os.path
from lxml import etree
from rest_framework.exceptions import ParseError

from ..settings import api_settings
from .exceptions import NotImplementedError

class Schema:

    def __init__(self, root):
        self.root = root

    @property
    def schema(self):
        return self.get_schema(self.root)

    def get_schema(self, root):
        """Returns xml schema to validata message

        Must redefine in subclasses"""

    def gen_structure_specific_schema(structures):
        pass

    def get_main_schema(self, version, schema_file):
        """Returns the schema to validate files"""
        path = os.path.join(
            api_settings.DEFAULT_SCHEMA_PATH, 'sdmx', 'ml', version, schema_file)
        try:
            tree = etree.parse(path)
        except (etree.ParseError, ValueError) as exc:
            raise ParseError('XML schema parse error - %s' % exc)
        return etree.XMLSchema(tree)

class Schema21(Schema):

    def get_schema(self, root):
        tag = root.tag
        if etree.QName(tag).localname.endswith('StructureSpecific'):
            raise NotImplementedError(
                detail='Schema generation for a {tag.localname} not yet implemented')
        else:
            schema = self.get_main_schema('2_1', 'SDMXMessage.xsd')
        return schema
