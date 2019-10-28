# managers.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    Format, Representation, ReferencePeriod
)

__all__ = []


if not is_model_registered('common', 'Format'):
    class Format(Format):
        pass

    __all__.append('Format')

if not is_model_registered('common', 'Representation'):
    class Representation(Representation):
        pass

    __all__.append('Representation')

if not is_model_registered('common', 'ReferencePeriod'):
    class ReferencePeriod(ReferencePeriod):
        pass

    __all__.append('ReferencePeriod')
