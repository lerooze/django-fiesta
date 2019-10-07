# renderer.py

import inspect

from rest_framework.renderers import BaseRenderer 
from rest_framework.exceptions import UnsupportedMediaType, ParseError
from lxml.etree import tostring
from lxml import etree
from typing import Iterable

from fiesta.utils.schema import Schema

from ...utils.coders import encode
from ...core.serializers.base import Serializer

class XMLRenderer(BaseRenderer):
    media_type = 'application/sdmx-ml'
    format = 'application/xml'

    def render(self, data, media_type=None, renderer_context=None):
        try:
            version = media_type.split(';')[1].split('=')[1]
        except (IndexError, AttributeError):
            version = '2.1'
        if version != '2.1':
            raise UnsupportedMediaType(media_type)
        data = data.unroll()
        query = getattr(data, '_query')
        if query.resource == 'schema':
            element = self.to_schema(data, query.context, query.observation_dimension)
        elif query.resource == 'data':
            pass
        else:
            element = self.to_structure_element(data, resource=query.resource, detail=query.detail)
            schema = Schema(element).schema
            if not schema(element):
                errors = [(error.line, error.domain, error.type, error.message) for error in schema.error_log]
                raise ParseError(errors)
        return tostring(element, xml_declaration=True) 

    def to_schema_element(self, serializer, context, observation_dimension):
        dsd = serializer.data_structure_list[0]
        data_structure_constraints = serializer.data_structure_list[0].content_constraint_list
        constraints = [constraint.unroll() for constraint in data_structure_constraints]
        if context in ['dataflow', 'provision_agreement']:
            dataflow_constraints = serializer.dataflow_list[0].content_constraint_list
            constraints.extend([constraint.unroll() for constraint in dataflow_constraints])
            if context == 'provision_agreement':
                provision_agreement_constraints = serializer.provision_agreement_list[0].content_constraint_list
                constraints.extend([constraint.unroll() for constraint in provision_agreement_constraints])

        def generate_simple_type():
            for dimension in dsd.dimension_list:



    def to_structure_element(self, serializer, field=None, resource=None, detail=None):
        """
        Renders into a lxml Element object.

        Parameters
        ----------
        serializer: Serializer
            The serializer instance to render
        field: Field
            The field of the dataclass for nested calls.
        resource: str  
            The resource keyword argument if the method is called via SDMX
            RESTful webservice call.
        detail: str 
            The detail keyword argument if the method is called via SDMX
            RESTful webservice calldata.
        """
        tag = field.metadata['fiesta'].tag if field else serializer._meta.tag

        # Fast field value lookup
        getval = lambda f: getattr(serializer, f.name, None)

        # Element detail full or stub
        as_stub = serializer.as_stub(serializer._meta, detail, resource) 

        # Get element attributes and create it
        attrib = serializer.to_attrs(as_stub)
        attrib = {key: value for key, value in attrib.items() if value}
        element = self.make_element(serializer, tag, attrib)
        
        # Add children elements
        for f in serializer._meta.non_attr_fields:
            if f.name != 'name' and as_stub: continue
            value = getval(f)
            if not value: continue
            field_meta = f.metadata['fiesta']
            # If it is a text element set its text
            if field_meta.is_text:
                element.text = encode(getval(f), f.type)
            elif inspect.isclass(f.type):
                if issubclass(f.type, Serializer):
                    child_serializer = getval(f) 
                    if not child_serializer: continue
                    element.append(self.to_structure_element(child_serializer, f, resource, detail))
                else:
                    child_tag = f.metadata['fiesta'].tag
                    child = etree.Element(child_tag)
                    child.text = encode(getval(f), f.type)
                    element.append(child)
            elif type(f.type) == type(Iterable):
                value = getval(f)
                element.extend(self.to_structure_element(item, f, resource, detail) 
                               for item in value)
            else:
                raise KeyError(f'Encountered an unknown type field: {f.type} while rendering as an element')
        return element

    def make_element(self, serializer, tag, attrib):
        return etree.Element(tag, attrib=attrib, nsmap=serializer._meta.nsmap)
