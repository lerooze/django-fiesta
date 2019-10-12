# managers.py

from oscar.core.loading import is_model_registered

from .abstract_models import MediumString, LargeString, Annotation, Format, Representation

__all__ = []

if not is_model_registered('common', 'MediumString'):
    class MediumString(MediumString):
        pass

    __all__.append('MediumString')

if not is_model_registered('common', 'LargeString'):
    class LargeString(LargeString):
        pass

    __all__.append('LargeString')

if not is_model_registered('common', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('common', 'Format'):
    class Format(Format):
        pass

    __all__.append('Format')

if not is_model_registered('common', 'Representation'):
    class Representation(Representation):
        pass

    __all__.append('Representation')
