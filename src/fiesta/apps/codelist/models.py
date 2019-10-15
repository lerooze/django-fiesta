# models.py

from oscar.core.loading import is_model_registered

from .abstract_models import CodelistReference, Codelist, Code

__all__ = []

if not is_model_registered('codelist', 'CodelistReference'):
    class CodelistReference(CodelistReference):
        pass

    __all__.append('CodelistReference')

if not is_model_registered('codelist', 'Codelist'):
    class Codelist(Codelist):
        pass

    __all__.append('Codelist')

if not is_model_registered('codelist', 'Code'):
    class Code(Code):
        pass

    __all__.append('Codelist')
