# user.py

import factory

from oscar.core.loading import get_model


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_model('base', 'user')

class OrganisationFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_model('base', 'organisation')

class ContactFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
