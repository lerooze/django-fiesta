# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation, AnnotationTranslation

from .models import DataStructure, Dataflow, Annotation 

translator.register(Annotation, AnnotationTranslation)
translator.register([DataStructure, Dataflow], NameableTranslation)
