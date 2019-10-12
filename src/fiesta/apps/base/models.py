# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    User, Text, Annotation, Versionable, Agency, DataProviderScheme,
    DataProvider, DataConsumerScheme, DataConsumer, OrganisationUnitScheme,
    OrganisationUnit, Contact, Telephone, Fax, X400, URI, Email
)


__all__ = []

if not is_model_registered('base', 'User'):
    class User(User):
        pass

    __all__.append('User')

if not is_model_registered('base', 'Text'):
    class Text(Text):
        pass

    __all__.append('Text')

if not is_model_registered('base', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('base', 'Versionable'):
    class Versionable(Versionable):
        pass

    __all__.append('Versionable')

if not is_model_registered('base', 'Agency'):
    class Agency(Agency):
        pass

    __all__.append('Agency')

if not is_model_registered('base', 'DataProviderScheme'):
    class DataProviderScheme(DataProviderScheme):
        pass

    __all__.append('DataProviderScheme')

if not is_model_registered('base', 'DataProvider'):
    class DataProvider(DataProvider):
        pass

    __all__.append('DataProvider')

if not is_model_registered('base', 'DataConsumerScheme'):
    class DataConsumerScheme(DataConsumerScheme):
        pass

    __all__.append('DataConsumerScheme')

if not is_model_registered('base', 'DataConsumer'):
    class DataConsumer(DataConsumer):
        pass

    __all__.append('DataConsumer')

if not is_model_registered('base', 'OrganisationUnitScheme'):
    class OrganisationUnitScheme(OrganisationUnitScheme):
        pass

    __all__.append('OrganisationUnitScheme')

if not is_model_registered('base', 'OrganisationUnit'):
    class OrganisationUnit(OrganisationUnit):
        pass

    __all__.append('OrganisationUnit')

if not is_model_registered('base', 'Contact'):
    class Contact(Contact):
        pass

    __all__.append('Contact')

if not is_model_registered('base', 'Telephone'):
    class Telephone(Telephone):
        pass

    __all__.append('Telephone')

if not is_model_registered('base', 'Fax'):
    class Fax(Fax):
        pass

    __all__.append('Fax')

if not is_model_registered('base', 'X400'):
    class X400(X400):
        pass

    __all__.append('X400')

if not is_model_registered('base', 'URI'):
    class URI(URI):
        pass

    __all__.append('URI')

if not is_model_registered('base', 'Email'):
    class Email(Email):
        pass

    __all__.append('Email')
