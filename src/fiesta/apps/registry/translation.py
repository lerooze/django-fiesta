# translation.py

from modeltranslation.translator import translator, TranslationOptions

from ..common.translation import (
    NameableTranslation, AnnotationTranslation
)

from .models import (
    Header, Party, Annotation, AttachmentConstraint,
    ContentConstraint, ProvisionAgreement
)

class HeaderTranslation(TranslationOptions):
    fields = ['name', 'source'] 

class PartyTranslation(TranslationOptions):
    fields = ['name'] 

translator.register(Annotation, AnnotationTranslation)
translator.register(Party, PartyTranslation)
translator.register([AttachmentConstraint, ContentConstraint, ProvisionAgreement], NameableTranslation)
translator.register(Header, HeaderTranslation)
