import os.path
from lxml import etree
from rest_framework.exceptions import ParseError

from ..settings import api_settings

class Schema:

    def __init__(self, root):
        self.root = root

    @property
    def schema(self):
        return self.get_schema(self.root)

    def get_schema(self, root):
        tag = root.tag
        specific = etree.QName(tag).localname.endswith('StructureSpecific')
        if specific:
            schema = self.gen_structure_specific_schema(root[0].findall(f'{{_ns["message"]}}Structure'))
        else:
            schema = self.get_main_schema()
        return schema

    def gen_structure_specific_schema(structures):
        pass

    def get_main_schema(self):
        """Returns the schema to validate files"""
        path = os.path.join(api_settings.SCHEMAS, 'SDMXMessage.xsd')
        try:
            tree = etree.parse(path)
        except (etree.ParseError, ValueError) as exc:
            raise ParseError('XML schema parse error - %s' % exc)
        return etree.XMLSchema(tree)
