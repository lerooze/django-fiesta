# translation.py

from modeltranslation.translator import translator, TranslationOptions

from ..common.translation import (
    NameableTranslation, ContactTranslation, AnnotationTranslation
)

from .models import (
    Header, Party, Contact, Annotation, AttachmentConstraint,
    ContentConstraint, ProvisionAgreement
)

class HeaderTranslation(TranslationOptions):
    fields = ['name', 'source'] 

translator.register(Annotation, AnnotationTranslation)
translator.register([Party, AttachmentConstraint, ContentConstraint, ProvisionAgreement], NameableTranslation)
translator.register(Contact, ContactTranslation)
translator.register(Header, HeaderTranslation)
