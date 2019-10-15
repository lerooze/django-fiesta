# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    ConceptSchemeReference, ConceptReference, ConceptScheme, Concept, ISOConceptReference
)

__all__ = []

if not is_model_registered('conceptscheme', 'ConceptSchemeReference'):
    class ConceptSchemeReference(ConceptSchemeReference):
        pass

    __all__.append('ConceptSchemeReferenceScheme')

if not is_model_registered('conceptscheme', 'ConceptReference'):
    class ConceptReference(ConceptReference):
        pass

    __all__.append('ConceptReferenceScheme')

if not is_model_registered('conceptscheme', 'ConceptScheme'):
    class ConceptScheme(ConceptScheme):
        pass

    __all__.append('ConceptScheme')

if not is_model_registered('conceptscheme', 'Concept'):
    class Concept(Concept):
        pass

    __all__.append('ConceptScheme')

if not is_model_registered('conceptscheme', 'ISOConceptReference'):
    class ISOConceptReference(ISOConceptReference):
        pass

    __all__.append('ISOConceptReference')

