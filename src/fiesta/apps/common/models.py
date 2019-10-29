# managers.py

from ...core.loading import is_model_registered

from .abstract_models import (
    Format, Representation, Contact
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

if not is_model_registered('common', 'Contact'):
    class Contact(Contact):
        pass

    __all__.append('Contact')
