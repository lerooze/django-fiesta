# translation.py

from modeltranslation.translator import translator, TranslationOptions
from .models import Annotation

class NameableTranslation(TranslationOptions):
    fields = ['name', 'description'] 

class AnnotationTranslation(TranslationOptions):
    fields = ['text'] 

class ContactTranslation(TranslationOptions):
    fields = ['name', 'department', 'role'] 

translator.register(Annotation, AnnotationTranslation)
