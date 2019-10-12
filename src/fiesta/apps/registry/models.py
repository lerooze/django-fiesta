from fiesta.apps.registry.abstract_models import (
    Text, Annotation, Log, SubmitStructureRequest, SubmittedStructure,
    StatusMessage, StatusMessageText, Header, Party, 
)
from oscar.core.loading import is_model_registered

__all__ = []

if not is_model_registered('registry', 'Text'):
    class Text(Text):
        pass

    __all__.append('Text')

if not is_model_registered('registry', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('registry', 'Log'):
    class Log(Log):
        pass

    __all__.append('Log')

if not is_model_registered('registry', 'SubmitStructureRequest'):
    class SubmitStructureRequest(SubmitStructureRequest):
        pass

    __all__.append('SubmitStructureRequest')

if not is_model_registered('registry', 'SubmittedStructure'):
    class SubmittedStructure(SubmittedStructure):
        pass

    __all__.append('SubmittedStructure')

if not is_model_registered('registry', 'StatusMessage'):
    class StatusMessage(StatusMessage):
        pass

    __all__.append('StatusMessage')

if not is_model_registered('registry', 'StatusMessageText'):
    class StatusMessageText(StatusMessageText):
        pass

    __all__.append('StatusMessageText')

if not is_model_registered('registry', 'Header'):
    class Header(Header):
        pass

    __all__.append('Header')

if not is_model_registered('registry', 'Party'):
    class Party(Party):
        pass

    __all__.append('Party')
