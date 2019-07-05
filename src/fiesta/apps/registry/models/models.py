from fiesta.apps.registry.models.abstract_models import (
    AbstractAcquisitionLog, AbstractQueryLog, AbstractSubmission,
    AbstractSubmitStructureRequest, AbstractSubmittedStructure,
    AbstractStatusMessage, AbstractStatusMessageText,
    AbstractRESTfulRegistration)
from fiesta.core.loading import is_model_registered

__all__ = []

if not is_model_registered('registry', 'AcquisitionLog'):
    class AcquisitionLog(AbstractAcquisitionLog):
        pass

    __all__.append('AcquisitionLog')

if not is_model_registered('registry', 'QueryLog'):
    class QueryLog(AbstractQueryLog):
        pass

    __all__.append('AcquisitionLog')

if not is_model_registered('registry', 'Submission'):
    class Submission(AbstractSubmission):
        pass

    __all__.append('Submission')

if not is_model_registered('registry', 'SubmitStructureRequest'):
    class Structure(AbstractSubmitStructureRequest):
        pass

    __all__.append('SubmitStructureRequest')

if not is_model_registered('registry', 'SubmittedStructure'):
    class SubmittedStructure(AbstractSubmittedStructure):
        pass

    __all__.append('SubmittedStructure')

if not is_model_registered('registry', 'StatusMessage'):
    class StatusMessage(AbstractStatusMessage):
        pass

    __all__.append('StatusMessage')

if not is_model_registered('registry', 'StatusMessageText'):
    class StatusMessageText(AbstractStatusMessageText):
        pass

    __all__.append('StatusMessageText')

if not is_model_registered('registry', 'RESTfulRegistration'):
    class RESTfulRegistration(AbstractRESTfulRegistration):
        pass

    __all__.append('RESTfulRegistration')
