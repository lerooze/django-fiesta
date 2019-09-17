# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    AbstractUser, AbstractOrganisationScheme, AbstractOrganisation,
    AbstractContact, AbstractTelephone, AbstractFax, AbstractX400, AbstractURI,
    AbstractEmail) 


__all__ = []

if not is_model_registered('base', 'User'):
    class User(AbstractUser):
        pass

    __all__.append('User')

if not is_model_registered('base', 'OrganisationScheme'):
    class OrganisationScheme(AbstractOrganisationScheme):
        pass

    __all__.append('OrganisationScheme')

if not is_model_registered('base', 'Organisation'):
    class Organisation(AbstractOrganisation):
        pass

    __all__.append('Organisation')

if not is_model_registered('base', 'Contact'):
    class Contact(AbstractContact):
        pass

    __all__.append('Contact')

if not is_model_registered('base', 'Telephone'):
    class Telephone(AbstractTelephone):
        pass

    __all__.append('Telephone')

if not is_model_registered('base', 'Fax'):
    class Fax(AbstractFax):
        pass

    __all__.append('Fax')

if not is_model_registered('base', 'X400'):
    class X400(AbstractX400):
        pass

    __all__.append('X400')

if not is_model_registered('base', 'URI'):
    class URI(AbstractURI):
        pass

    __all__.append('URI')

if not is_model_registered('base', 'Email'):
    class Email(AbstractEmail):
        pass

    __all__.append('Email')
