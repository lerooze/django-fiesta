
from fiesta.apps.codelist.models.abstract import AbstractCodelist, AbstractCode
from fiesta.core.loading import is_model_registered

__all__ = []

if not is_model_registered('codelist', 'Codelist'):
    class Codelist(AbstractCodelist):
        pass

    __all__.append('Codelist')

if not is_model_registered('codelist', 'Code'):
    class Code(AbstractCode):
        pass

    __all__.append('Codelist')
