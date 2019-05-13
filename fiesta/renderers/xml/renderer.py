
from rest_framework.renderers import BaseRenderer 
from rest_framework.exceptions import UnsupportedMediaType, ParseError
from lxml.etree import tostring, QName

from ...utils.schema import Schema
from ... import constants


class XMLRenderer(BaseRenderer):
    media_type = 'application/sdmx-ml'
    format = 'application/xml'

    def get_tag(self, data):
        if 'RegistryInterface' in data.__class__.__name__:
            return QName(constants.NAMESPACE['message'], 'RegistryInterface').text

    def render(self, data, media_type=None, renderer_context=None):
        try:
            version = media_type.split(';')[1].split('=')[1]
        except (IndexError, AttributeError):
            version = '2.1'
        if version != '2.1':
            raise UnsupportedMediaType(media_type)
        tag = self.get_tag(data)
        data = data.unroll()
        element = data.to_element(tag)
        schema = Schema(element).schema
        if not schema(element):
            errors = [(error.line, error.domain, error.type, error.message) for error in schema.error_log]
            raise ParseError(errors)
        return tostring(element, xml_declaration=True) 
