# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import Text, Annotation, Versionable, Codelist, Code

__all__ = []

if not is_model_registered('base', 'Text'):
    class Text(Text):
        pass

    __all__.append('Text')

if not is_model_registered('base', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('base', 'Versionable'):
    class Versionable(Versionable):
        pass

    __all__.append('Versionable')

if not is_model_registered('codelist', 'Codelist'):
    class Codelist(Codelist):
        pass

    __all__.append('Codelist')

if not is_model_registered('codelist', 'Code'):
    class Code(Code):
        pass

    __all__.append('Codelist')
