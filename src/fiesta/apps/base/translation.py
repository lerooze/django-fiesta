# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation, ContactTranslation

from .models import (
    Agency, AgencyContact, DataProviderScheme, DataProvider,
    DataProviderContact, DataConsumerScheme, DataConsumer, DataConsumerContact,
    OrganisationUnitScheme, OrganisationUnit, OrganisationUnitContact 
)


translator.register([Agency, DataProviderScheme, DataProvider, DataConsumerScheme, DataConsumer, OrganisationUnitScheme, OrganisationUnit], NameableTranslation)
translator.register([AgencyContact, DataProviderContact, DataConsumerContact, OrganisationUnitContact], ContactTranslation)
