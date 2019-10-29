# models.py

from ...core.loading import is_model_registered

from .abstract_models import (
    User, 
    Annotation, 
    Agency,
    DataProviderScheme,
    DataProvider,
    DataConsumerScheme,
    DataConsumer,
    OrganisationUnitScheme,
    OrganisationUnit
)


__all__ = []

if not is_model_registered('base', 'User'):
    class User(User):
        pass

    __all__.append('User')

__all__ = []

if not is_model_registered('base', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

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
