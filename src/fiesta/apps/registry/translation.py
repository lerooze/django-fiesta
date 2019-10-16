# translation.py

from modeltranslation.translator import translator, TranslationOptions

from ..common.translation import NameableTranslation, ContactTranslation

from .models import (
    Header, Party, Contact, AttachmentConstraint, ContentConstraint,
    ProvisionAgreement
)

class HeaderTranslation(TranslationOptions):
    fields = ['name', 'source'] 

translator.register([Party, AttachmentConstraint, ContentConstraint, ProvisionAgreement], NameableTranslation)
translator.register(Contact, ContactTranslation)
translator.register(Header, HeaderTranslation)
