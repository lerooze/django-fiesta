# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    Annotation, ConceptSchemeReference, ConceptReference, ConceptScheme,
    Concept, ISOConceptReference
)

__all__ = []

if not is_model_registered('conceptscheme', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('conceptscheme', 'ConceptSchemeReference'):
    class ConceptSchemeReference(ConceptSchemeReference):
        pass

    __all__.append('ConceptSchemeReference')

if not is_model_registered('conceptscheme', 'ConceptReference'):
    class ConceptReference(ConceptReference):
        pass

    __all__.append('ConceptReference')

if not is_model_registered('conceptscheme', 'ConceptScheme'):
    class ConceptScheme(ConceptScheme):
        pass

    __all__.append('ConceptScheme')

if not is_model_registered('conceptscheme', 'Concept'):
    class Concept(Concept):
        pass

    __all__.append('Concept')

if not is_model_registered('conceptscheme', 'ISOConceptReference'):
    class ISOConceptReference(ISOConceptReference):
        pass

    __all__.append('ISOConceptReference')

