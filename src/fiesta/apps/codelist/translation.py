# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation, AnnotationTranslation

from .models import Annotation, Codelist, Code

translator.register(Annotation, AnnotationTranslation)
translator.register([Codelist, Code], NameableTranslation)
