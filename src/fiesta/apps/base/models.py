# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    User, Agency, AgencyContact, AgencyContactTelephone, AgencyContactFax,
    AgencyContactX400, AgencyContactEmail, AgencyContactURI,
    DataProviderScheme, DataProviderReference, DataProvider,
    DataProviderContact, DataProviderContactTelephone, DataProviderContactFax,
    DataProviderContactX400, DataProviderContactEmail, DataProviderContactURI,
    DataConsumerScheme, DataConsumer, DataConsumerContact,
    DataConsumerContactTelephone, DataConsumerContactFax,
    DataConsumerContactX400, DataConsumerContactEmail, DataConsumerContactURI,
    OrganisationUnitScheme, OrganisationUnit, OrganisationUnitContact,
    OrganisationUnitContactTelephone, OrganisationUnitContactFax,
    OrganisationUnitContactX400, OrganisationUnitContactEmail,
    OrganisationUnitContactURI
)


__all__ = []

if not is_model_registered('base', 'User'):
    class User(User):
        pass

    __all__.append('User')

if not is_model_registered('base', 'Agency'):
    class Agency(Agency):
        pass

    __all__.append('Agency')

if not is_model_registered('base', 'AgencyContact'):
    class AgencyContact(AgencyContact):
        pass

    __all__.append('AgencyContact')

if not is_model_registered('base', 'AgencyContactTelephone'):
    class AgencyContactTelephone(AgencyContactTelephone):
        pass

    __all__.append('AgencyContactTelephone')

if not is_model_registered('base', 'AgencyContactFax'):
    class AgencyContactFax(AgencyContactFax):
        pass

    __all__.append('AgencyContactFax')

if not is_model_registered('base', 'AgencyContactX400'):
    class AgencyContactX400(AgencyContactX400):
        pass

    __all__.append('AgencyContactX400')

if not is_model_registered('base', 'AgencyContactEmail'):
    class AgencyContactEmail(AgencyContactEmail):
        pass

    __all__.append('AgencyContactEmail')

if not is_model_registered('base', 'AgencyContactURI'):
    class AgencyContactURI(AgencyContactURI):
        pass

    __all__.append('AgencyContactURI')

if not is_model_registered('base', 'DataProviderScheme'):
    class DataProviderScheme(DataProviderScheme):
        pass

    __all__.append('DataProviderScheme')

if not is_model_registered('base', 'DataProviderReference'):
    class DataProviderReference(DataProviderReference):
        pass

    __all__.append('DataProviderReference')

if not is_model_registered('base', 'DataProvider'):
    class DataProvider(DataProvider):
        pass

    __all__.append('DataProvider')

if not is_model_registered('base', 'DataProviderContact'):
    class DataProviderContact(DataProviderContact):
        pass

    __all__.append('DataProviderContact')

if not is_model_registered('base', 'DataProviderContactTelephone'):
    class DataProviderContactTelephone(DataProviderContactTelephone):
        pass

    __all__.append('DataProviderContactTelephone')

if not is_model_registered('base', 'DataProviderContactFax'):
    class DataProviderContactFax(DataProviderContactFax):
        pass

    __all__.append('DataProviderContactFax')

if not is_model_registered('base', 'DataProviderContactX400'):
    class DataProviderContactX400(DataProviderContactX400):
        pass

    __all__.append('DataProviderContactX400')

if not is_model_registered('base', 'DataProviderContactEmail'):
    class DataProviderContactEmail(DataProviderContactEmail):
        pass

    __all__.append('DataProviderContactEmail')

if not is_model_registered('base', 'DataProviderContactURI'):
    class DataProviderContactURI(DataProviderContactURI):
        pass

    __all__.append('DataProviderContactURI')

if not is_model_registered('base', 'DataConsumerScheme'):
    class DataConsumerScheme(DataConsumerScheme):
        pass

    __all__.append('DataConsumerScheme')

if not is_model_registered('base', 'DataConsumer'):
    class DataConsumer(DataConsumer):
        pass

    __all__.append('DataConsumer')

if not is_model_registered('base', 'DataConsumerContact'):
    class DataConsumerContact(DataConsumerContact):
        pass

    __all__.append('DataConsumerContact')

if not is_model_registered('base', 'DataConsumerContactTelephone'):
    class DataConsumerContactTelephone(DataConsumerContactTelephone):
        pass

    __all__.append('DataConsumerContactTelephone')

if not is_model_registered('base', 'DataConsumerContactFax'):
    class DataConsumerContactFax(DataConsumerContactFax):
        pass

    __all__.append('DataConsumerContactFax')

if not is_model_registered('base', 'DataConsumerContactX400'):
    class DataConsumerContactX400(DataConsumerContactX400):
        pass

    __all__.append('DataConsumerContactX400')

if not is_model_registered('base', 'DataConsumerContactEmail'):
    class DataConsumerContactEmail(DataConsumerContactEmail):
        pass

    __all__.append('DataConsumerContactEmail')

if not is_model_registered('base', 'DataConsumerContactURI'):
    class DataConsumerContactURI(DataConsumerContactURI):
        pass

    __all__.append('DataConsumerContactURI')

if not is_model_registered('base', 'OrganisationUnitScheme'):
    class OrganisationUnitScheme(OrganisationUnitScheme):
        pass

    __all__.append('OrganisationUnitScheme')

if not is_model_registered('base', 'OrganisationUnit'):
    class OrganisationUnit(OrganisationUnit):
        pass

    __all__.append('OrganisationUnit')

if not is_model_registered('base', 'OrganisationUnitContact'):
    class OrganisationUnitContact(OrganisationUnitContact):
        pass

    __all__.append('OrganisationUnitContact')

if not is_model_registered('base', 'OrganisationUnitContactTelephone'):
    class OrganisationUnitContactTelephone(OrganisationUnitContactTelephone):
        pass

    __all__.append('OrganisationUnitContactTelephone')

if not is_model_registered('base', 'OrganisationUnitContactFax'):
    class OrganisationUnitContactFax(OrganisationUnitContactFax):
        pass

    __all__.append('OrganisationUnitContactFax')

if not is_model_registered('base', 'OrganisationUnitContactX400'):
    class OrganisationUnitContactX400(OrganisationUnitContactX400):
        pass

    __all__.append('OrganisationUnitContactX400')

if not is_model_registered('base', 'OrganisationUnitContactEmail'):
    class OrganisationUnitContactEmail(OrganisationUnitContactEmail):
        pass

    __all__.append('OrganisationUnitContactEmail')

if not is_model_registered('base', 'OrganisationUnitContactURI'):
    class OrganisationUnitContactURI(OrganisationUnitContactURI):
        pass

    __all__.append('OrganisationUnitContactURI')
