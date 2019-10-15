# managers.py

from oscar.core.loading import is_model_registered

from .abstract_models import (
    SmallString, URLString, EmailString, Annotation, Format,
    Representation, ReferencePeriod
)

__all__ = []

if not is_model_registered('common', 'SmallString'):
    class SmallString(SmallString):
        pass

    __all__.append('SmallString')

if not is_model_registered('common', 'URLString'):
    class URLString(URLString):
        pass

    __all__.append('URLString')

if not is_model_registered('common', 'EmailString'):
    class EmailString(EmailString):
        pass

    __all__.append('EmailString')

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

if not is_model_registered('common', 'ReferencePeriod'):
    class ReferencePeriod(ReferencePeriod):
        pass

    __all__.append('ReferencePeriod')
