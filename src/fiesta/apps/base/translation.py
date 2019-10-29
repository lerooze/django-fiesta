# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation, AnnotationTranslation

from .models import (
    Annotation, 
    Agency, 
    DataProviderScheme, 
    DataProvider,
    DataConsumerScheme, 
    DataConsumer, 
    OrganisationUnitScheme, 
    OrganisationUnit
)

translator.register(Annotation, AnnotationTranslation)

translator.register([Agency, DataProviderScheme, DataProvider, DataConsumerScheme, DataConsumer, OrganisationUnitScheme, OrganisationUnit], NameableTranslation)
