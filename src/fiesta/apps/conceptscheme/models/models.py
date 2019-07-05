
from fiesta.apps.conceptscheme.models.abstract import (AbstractConceptScheme,
                                                       AbstractConcept,
                                                       AbstractISOConceptReference)
from fiesta.core.loading import is_model_registered

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

