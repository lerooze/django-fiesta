from fiesta.apps.registry.abstract_models import (
    AbstractAcquisitionLog, AbstractQueryLog, AbstractSubmission,
    AbstractSubmitStructureRequest, AbstractSubmittedStructure,
    AbstractStatusMessage, AbstractStatusMessageText,
    AbstractRESTfulStructureQuery, AbstractRESTfulSchemaQuery,
    AbstractProvisionAgreement
)
from oscar.core.loading import is_model_registered

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
    class SubmitStructureRequest(AbstractSubmitStructureRequest):
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

if not is_model_registered('registry', 'RESTfulStructureQuery'):
    class RESTfulStructureQuery(AbstractRESTfulStructureQuery):
        pass

    __all__.append('RESTfulStructureQuery')

if not is_model_registered('registry', 'RESTfulSchemaQuery'):
    class RESTfulSchemaQuery(AbstractRESTfulSchemaQuery):
        pass

    __all__.append('RESTfulSchemaQuery')

if not is_model_registered('registry', 'ProvisionAgreement'):
    class ProvisionAgreement(AbstractProvisionAgreement):
        pass

    __all__.append('ProvisionAgreement')
