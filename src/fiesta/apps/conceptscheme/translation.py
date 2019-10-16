# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation

from .models import ConceptScheme, Concept

translator.register([ConceptScheme, Concept], NameableTranslation)
