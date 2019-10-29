# translation.py

from modeltranslation.translator import TranslationOptions, translator

from .models import Contact

class NameableTranslation(TranslationOptions):
    fields = ['name', 'description'] 

class AnnotationTranslation(TranslationOptions):
    fields = ['text'] 

class ContactTranslation(TranslationOptions):
    fields = ['name', 'department', 'role'] 

translator.register(Contact, ContactTranslation)
