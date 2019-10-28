# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation, AnnotationTranslation, ContactTranslation

from .models import (
    Annotation, Agency, AgencyContact, DataProviderScheme, DataProvider,
    DataProviderContact, DataConsumerScheme, DataConsumer, DataConsumerContact,
    OrganisationUnitScheme, OrganisationUnit, OrganisationUnitContact 
)

translator.register(Annotation, AnnotationTranslation)

translator.register([Agency, DataProviderScheme, DataProvider, DataConsumerScheme, DataConsumer, OrganisationUnitScheme, OrganisationUnit], NameableTranslation)
translator.register([AgencyContact, DataProviderContact, DataConsumerContact, OrganisationUnitContact], ContactTranslation)
