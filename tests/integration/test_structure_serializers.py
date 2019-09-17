# test_xml_parser.py

import os
import pytest

from fiesta.parsers import XMLParser
from fiesta.core.serializers import structure

@pytest.fixture(scope='session')
def xml_parser():
    return XMLParser()

@pytest.fixture(scope='session')
def path_serializer(request, xml_parser):
    def _path_serializer(filename):
        path = os.path.join(request.config.rootdir, 'tests', 'data', filename)
        obj = xml_parser.get(path)
        obj.unroll()
        return obj
    return _path_serializer

@pytest.fixture(scope='session')
def org_scheme(path_serializer):
    return path_serializer('org_schemes.xml')

@pytest.fixture(scope='session')
def org_scheme_submit(org_scheme):
    return org_scheme.to_request()

@pytest.fixture(scope='session')
def org_scheme_submit_elem(org_scheme_submit):
    return org_scheme_submit.to_element()

@pytest.fixture(scope='session')
def org_scheme_re_submit(org_scheme_submit_elem):
    return structure.RegistryInterfaceSubmitStructureRequestSerializer(org_scheme_submit_elem)


class TestOrganisationSchemeStructureSerializer:

    def test_sdmx_message_serializes_into_structure_serializer(self, org_scheme):
        assert isinstance(org_scheme, structure.Serializer)

    def test_agency_scheme_id_equals_to_AGENCIES(self, org_scheme):
        agencies = org_scheme.structures.organisation_schemes.agency_scheme[0].object_id
        assert agencies == 'AGENCIES'

    def test_agency_scheme_name_equals_to_Agencies(self, org_scheme):
        name = org_scheme.structures.organisation_schemes.agency_scheme[0].name[0].text
        assert name == 'Agencies'

    def test_submit_id_equals_to_SID1(self, org_scheme_submit):
        assert org_scheme_submit.header.object_id == 'SID1'
    def test_meta_repr_raises_no_exception(self, org_scheme_submit):
        repr(org_scheme_submit._meta)

    def test_to_element_method_raises_no_exception(self, org_scheme_submit):
        org_scheme_submit.to_element()

    def test_serializer_unrolls(self, org_scheme_re_submit):
        org_scheme_re_submit.unroll()

@pytest.fixture(scope='session')
def dsd_scheme(path_serializer):
    return path_serializer('dsd_ecb_ivf1.xml')

@pytest.fixture(scope='session')
def dsd_scheme_submit(dsd_scheme):
    return dsd_scheme.to_request()

@pytest.fixture(scope='session')
def dsd_scheme_submit_elem(dsd_scheme_submit):
    return dsd_scheme_submit.to_element()

@pytest.fixture(scope='session')
def dsd_scheme_re_submit(dsd_scheme_submit_elem):
    return structure.RegistryInterfaceSubmitStructureRequestSerializer(dsd_scheme_submit_elem)

class TestDataStructureSerializer:

    def test_sdmx_message_serializes_into_structure_serializer(self, dsd_scheme):
        assert isinstance(dsd_scheme, structure.Serializer)

    def test_agency_scheme_id_equals_to_ECB_IVF1(self, dsd_scheme):
        object_id = dsd_scheme.structures.data_structures.data_structure[0].object_id
        assert object_id == 'ECB_IVF1'

    def test_dsd_name_equals_to_Investment_Funds(self, dsd_scheme):
        name = dsd_scheme.structures.data_structures.data_structure[0].name[0].text
        assert name == 'Investment Funds'

    def test_submit_id_equals_to_SID1(self, dsd_scheme_submit):
        assert dsd_scheme_submit.header.object_id == 'SID1'

    def test_meta_repr_raises_no_exception(self, dsd_scheme_submit):
        repr(dsd_scheme_submit._meta)

    def test_to_element_method_raises_no_exception(self, dsd_scheme_submit):
        dsd_scheme_submit.to_element()

    def test_serializer_unrolls(self, dsd_scheme_re_submit):
        dsd_scheme_re_submit.unroll()

    def test_first_dimension_concept_identity_object_id_equals_to_FREQ(sef, dsd_scheme):
        dimensions = dsd_scheme.structures.data_structures.data_structure[0].data_structure_components.dimension_list.dimension
        dimension = dimensions[0]
        assert dimension.concept_identity.ref.object_id == 'FREQ'

    def test_first_group_dimension_object_id_equals_to_REF_AREA(sef, dsd_scheme):
        groups = dsd_scheme.structures.data_structures.data_structure[0].data_structure_components.group[0].group_dimension
        group_dimension = groups[0]
        assert group_dimension.dimension_reference.ref.object_id == 'REF_AREA'

    def test_first_attribute_concept_identity_object_id_equals_to_TIME_FORMAT(sef, dsd_scheme):
        attributes = dsd_scheme.structures.data_structures.data_structure[0].data_structure_components.attribute_list.attribute
        attribute = attributes[0]
        assert attribute.concept_identity.ref.object_id == 'TIME_FORMAT'
