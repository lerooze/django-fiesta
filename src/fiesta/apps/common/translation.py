# translation.py

from modeltranslation.translator import TranslationOptions

class NameableTranslation(TranslationOptions):
    fields = ['name', 'description'] 

class AnnotationTranslation(TranslationOptions):
    fields = ['text'] 

class ContactTranslation(TranslationOptions):
    fields = ['name', 'department', 'role'] 
