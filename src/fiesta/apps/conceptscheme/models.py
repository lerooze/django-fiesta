# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    AbstractConceptScheme, AbstractConcept, AbstractISOConceptReference)

__all__ = []

if not is_model_registered('conceptscheme', 'ConceptScheme'):
    class ConceptScheme(AbstractConceptScheme):
        pass

    __all__.append('ConceptScheme')

if not is_model_registered('conceptscheme', 'Concept'):
    class Concept(AbstractConcept):
        pass

    __all__.append('ConceptScheme')

if not is_model_registered('conceptscheme', 'ISOConceptReference'):
    class ISOConceptReference(AbstractISOConceptReference):
        pass

    __all__.append('ISOConceptReference')

