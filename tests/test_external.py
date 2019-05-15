from unittest import TestCase

from fiesta.parsers import XMLParser
from fiesta import structure

import pytest


class OrganisationSchemeExternalTest(TestCase):
    
    @pytest.mark.django_db
    def setUp(self):
        self.location = 'https://sdw-wsrest.ecb.europa.eu/service/organisationscheme/SDMX/AGENCIES'
        self.parser = XMLParser()
        self.obj = self.parser.get(self.location)
        self.obj.unroll()
        self.request_object = self.obj.to_request()
        self.request_element = self.request_object.to_element(unroll=True)
        self.request_object_round_trip = structure.RegistryInterfaceSubmitStructureRequest(
            element=self.request_element)
        self.request_object_round_trip.unroll()

    def test_methods(self):
        self.assertIsInstance(self.obj, structure.Structure)
        obj = self.obj.structures
        self.assertIsInstance(obj, structure.Structures)
        obj = obj.organisation_schemes
        self.assertIsInstance(obj, structure.OrganisationSchemes)
        obj.agency_scheme = list(obj.agency_scheme)
        obj = obj.agency_scheme[0]
        self.assertIsInstance(obj, structure.AgencyScheme)
        obj.agency = list(obj.agency)
        obj = obj.agency[0]
        self.assertIsInstance(obj, structure.Agency)
        object_id = obj.object_id
        self.assertIsNotNone(object_id)
        self.assertIsInstance(object_id, str)

    def test_identical_structures(self):
        struct1 = self.obj.structures 
        struct2 = self.request_object.submit_structure_request.structures
        struct3 = self.request_object_round_trip.submit_structure_request.structures
        self.assertEqual(struct1, struct2)
        self.assertEqual(struct2, struct3)
