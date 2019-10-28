# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation, AnnotationTranslation

from .models import ConceptScheme, Concept, Annotation

translator.register(Annotation, AnnotationTranslation)
translator.register([ConceptScheme, Concept], NameableTranslation)
