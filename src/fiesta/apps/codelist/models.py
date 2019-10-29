# models.py

from ...core.loading import is_model_registered

from .abstract_models import Annotation, Codelist, Code

__all__ = []

if not is_model_registered('codelist', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('codelist', 'Codelist'):
    class Codelist(Codelist):
        pass

    __all__.append('Codelist')

if not is_model_registered('codelist', 'Code'):
    class Code(Code):
        pass

    __all__.append('Code')
