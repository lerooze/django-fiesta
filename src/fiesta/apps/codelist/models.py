# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import AbstractCodelist, AbstractCode

__all__ = []

if not is_model_registered('codelist', 'Codelist'):
    class Codelist(AbstractCodelist):
        pass

    __all__.append('Codelist')

if not is_model_registered('codelist', 'Code'):
    class Code(AbstractCode):
        pass

    __all__.append('Codelist')
