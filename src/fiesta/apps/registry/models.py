from fiesta.apps.registry.abstract_models import (
    Log, SubmitStructureRequest, SubmittedStructure, StatusMessage,
    ErrorCode, Header, Structure, Party, Contact, Telephone, Fax, X400, Email,
    URI, ProvisionAgreementReference, ProvisionAgreement,
    AttachmentConstraintReference, AttachmentConstraint,
    ContentConstraintReference, ContentConstraint, KeySet, Key, SubKey,
    CubeRegion, CubeRegionKey, CubeRegionKeyValue, CubeRegionKeyTimeRange,
    TimePeriod, ReleaseCalendar   
)
from oscar.core.loading import is_model_registered

__all__ = []

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

if not is_model_registered('registry', 'ErrorCode'):
    class ErrorCode(ErrorCode):
        pass

    __all__.append('ErrorCode')

if not is_model_registered('registry', 'Header'):
    class Header(Header):
        pass

    __all__.append('Header')

if not is_model_registered('registry', 'Structure'):
    class Structure(Structure):
        pass

    __all__.append('Structure')

if not is_model_registered('registry', 'Party'):
    class Party(Party):
        pass

    __all__.append('Party')

if not is_model_registered('registry', 'Contact'):
    class Contact(Contact):
        pass

    __all__.append('Contact')

if not is_model_registered('registry', 'Telephone'):
    class Telephone(Telephone):
        pass

    __all__.append('Telephone')

if not is_model_registered('registry', 'Fax'):
    class Fax(Fax):
        pass

    __all__.append('Fax')

if not is_model_registered('registry', 'X400'):
    class X400(X400):
        pass

    __all__.append('X400')

if not is_model_registered('registry', 'Email'):
    class Email(Email):
        pass

    __all__.append('Email')

if not is_model_registered('registry', 'URI'):
    class URI(URI):
        pass

    __all__.append('URI')

if not is_model_registered('registry', 'ProvisionAgreementReference'):
    class ProvisionAgreementReference(ProvisionAgreementReference):
        pass

    __all__.append('ProvisionAgreementReference')

if not is_model_registered('registry', 'ProvisionAgreement'):
    class ProvisionAgreement(ProvisionAgreement):
        pass

    __all__.append('ProvisionAgreement')

if not is_model_registered('registry', 'AttachmentConstraintReference'):
    class AttachmentConstraintReference(AttachmentConstraintReference):
        pass

    __all__.append('AttachmentConstraintReference')

if not is_model_registered('registry', 'AttachmentConstraint'):
    class AttachmentConstraint(AttachmentConstraint):
        pass

    __all__.append('AttachmentConstraint')

if not is_model_registered('registry', 'ContentConstraintReference'):
    class ContentConstraintReference(ContentConstraintReference):
        pass

    __all__.append('ContentConstraintReference')

if not is_model_registered('registry', 'ContentConstraint'):
    class ContentConstraint(ContentConstraint):
        pass

    __all__.append('ContentConstraint')

if not is_model_registered('registry', 'KeySet'):
    class KeySet(KeySet):
        pass

    __all__.append('KeySet')

if not is_model_registered('registry', 'Key'):
    class Key(Key):
        pass

    __all__.append('Key')

if not is_model_registered('registry', 'SubKey'):
    class SubKey(SubKey):
        pass

    __all__.append('SubKey')

if not is_model_registered('registry', 'CubeRegion'):
    class CubeRegion(CubeRegion):
        pass

    __all__.append('CubeRegion')

if not is_model_registered('registry', 'CubeRegionKey'):
    class CubeRegionKey(CubeRegionKey):
        pass

    __all__.append('CubeRegionKey')

if not is_model_registered('registry', 'CubeRegionKeyValue'):
    class CubeRegionKeyValue(CubeRegionKeyValue):
        pass

    __all__.append('CubeRegionKeyValue')

if not is_model_registered('registry', 'CubeRegionKeyTimeRange'):
    class CubeRegionKeyTimeRange(CubeRegionKeyTimeRange):
        pass

    __all__.append('CubeRegionKeyTimeRange')

if not is_model_registered('registry', 'TimePeriod'):
    class TimePeriod(TimePeriod):
        pass

    __all__.append('TimePeriod')

if not is_model_registered('registry', 'ReleaseCalendar'):
    class ReleaseCalendar(ReleaseCalendar):
        pass

    __all__.append('ReleaseCalendar')
