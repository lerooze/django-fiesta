
from django.contrib.auth.models import User
from lxml import etree
from rest_framework.test import APITestCase
from fiesta import constants
from fiesta import models
from fiesta.parsers import XMLParser
import pytest


class SetUpMixin:

    @pytest.mark.django_db
    def setUp(self):
        ecb_user, _ = User.objects.get_or_create(username='neosdmx.ecb@gmail.com',
                                             first_name='NeoSDMX',
                                             last_name='ECB',
                                             email='neosdmx.ecb@gmail.com',
                                             password='pass')
        sdmx_user, _ = User.objects.get_or_create(username='neosdmx.sdmx@gmail.com',
                                             first_name='NeoSDMX',
                                             last_name='SDMX',
                                             email='neosdmx.sdmx@gmail.com',
                                             password='pass')
        sdmx, _ = models.Organisation.objects.get_or_create(object_id='SDMX')
        ecb, _ = models.Organisation.objects.get_or_create(object_id='ECB')
        models.Contact.objects.get_or_create(user=sdmx_user, organisation=sdmx)
        models.Contact.objects.get_or_create(user=ecb_user, organisation=ecb)
        self.client.force_login(ecb_user)
        self.parser = XMLParser()

class InitialSetUp(SetUpMixin, APITestCase):

    def setUp(self):
        super().setUp()

    def test_setup_user(self):
        user = User.objects.get(username='neosdmx.sdmx@gmail.com')
        self.assertRecordValues(user,  {'first_name': 'NeoSDMX', 'last_name': 'SDMX'})

    def test_setup_organisation(self):
        organisation = models.Organisation.objects.get(object_id='ECB')
        self.assertRecordValues(organisation,  {'object_id': 'ECB'})

    def assertRecordValues(self, record, values_dict):
        for key, value in values_dict.items():
            self.assertEqual(getattr(record, key), value)

class OrganisationRequestTest(SetUpMixin, APITestCase):

    def setUp(self):
        super().setUp()
        location = 'https://sdw-wsrest.ecb.europa.eu/service/organisationscheme/SDMX/AGENCIES'
        obj = self.parser.get(location)
        request_object = obj.to_request()
        tag = etree.QName(constants.NAMESPACE['message'], 'RegistryInterface').text
        request_element = request_object.to_element(tag)
        xml = etree.tostring(request_element, xml_declaration=True, encoding='utf-8')
        self.response = self.client.post('/fiesta/wsreg/SubmitStructure/',
                                         xml,
                                         content_type='application/sdmxml')

    def test_post_organisation_scheme(self):
        self.assertEqual(self.response.status_code, 200)

    def tearDown(self):
        self.client.logout()
