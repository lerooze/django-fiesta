# test_xml_parser.py


# class OrganisationSchemeExternalTest(TestCase):
#     
#     def setUp(self):
#         self.parser = XMLParser()
#         self.obj = self.parser.get(os.path.join(pkg_path, self.location)
#         self.obj.unroll()
#         self.request_object = self.obj.to_request()
#         self.request_element = self.request_object.to_element()
#         self.request_object_round_trip = structure.RegistryInterfaceSubmitStructureRequestDataclass(
#             element=self.request_element)
#         self.request_object_round_trip.unroll()
#
#     def test_methods(self):
#         self.assertIsInstance(self.obj, structure.StructureDataclass)
#         obj = self.obj.structures
#         self.assertIsInstance(obj, structure.StructuresDataclass)
#         obj = obj.organisation_schemes
#         self.assertIsInstance(obj, structure.OrganisationSchemesDataclass)
#         obj.agency_scheme = list(obj.agency_scheme)
#         obj = obj.agency_scheme[0]
#         self.assertIsInstance(obj, structure.AgencySchemeDataclass)
#         obj.agency = list(obj.agency)
#         obj = obj.agency[0]
#         self.assertIsInstance(obj, structure.AgencyDataclass)
#         object_id = obj.object_id
#         self.assertIsNotNone(object_id)
#         self.assertIsInstance(object_id, str)
#
#     def test_identical_structures(self):
#         struct1 = self.obj.structures 
#         struct2 = self.request_object.submit_structure_request.structures
#         struct3 = self.request_object_round_trip.submit_structure_request.structures
#         self.assertEqual(struct1, struct2)
#         self.assertEqual(struct2, struct3)
