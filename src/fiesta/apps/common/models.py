# managers.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    AbstractText, AbstractAnnotation, AbstractFormat, AbstractRepresentation,
    AbstractReferencePeriod)

__all__ = []

if not is_model_registered('common', 'Text'):
    class Text(AbstractText):
        pass

    __all__.append('Text')

if not is_model_registered('common', 'Annotation'):
    class Annotation(AbstractAnnotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('common', 'Format'):
    class Format(AbstractFormat):
        pass

    __all__.append('Format')

if not is_model_registered('common', 'Representation'):
    class Representation(AbstractRepresentation):
        pass

    __all__.append('Representation')

if not is_model_registered('common', 'ReferencePeriod'):
    class ReferencePeriod(AbstractReferencePeriod):
        pass

    __all__.append('ReferencePeriod')
