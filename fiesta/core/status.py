from dataclasses import dataclass
from django.utils.translation import gettext as _

@dataclass
class CommonStatusMessage:
    code: int
    text: str 

#444
FIESTA_1001_HEADER_ORGANISATION_NOT_REGISTERED = CommonStatusMessage(
    1001,
    _('Header organisation not registered and will be recorded as missing')
)

#442
FIESTA_1002_HEADER_CONTACT_EMAIL_NOT_FOUND = CommonStatusMessage(
    1002,
    _('Header contact email not found and contact will not be recorded')
)
#451
FIESTA_1003_USER_NOT_IN_ORGANISATION = CommonStatusMessage(
    1003,
    _('User not a member of header organisation')
)
#453
FIESTA_1004_CONTACT_NOT_REGISTERED = CommonStatusMessage(
    1004,
    _('Provided Header contact is not registered and will not be recorded')
)
#461
FIESTA_1101_NOT_PROCESSED_FOOTER_ERRORS = CommonStatusMessage(
    1101,
    _('Footer error: No payload was generated')
)

#411
FIESTA_2101_MODIFICATION_NOT_ALLOWED = CommonStatusMessage(
    2101,
    _('Modidication of final versionable strutures not allowed')
)

#412
FIESTA_2102_APPENDING_NOT_ALLOWED = CommonStatusMessage(
    2102,
    _('Appending to already existing structures not allowed')
)

#421
FIESTA_2103_SOAP_PULLING_NOT_IMPLEMENTED = CommonStatusMessage(
    2103,
    _('SOAP structure pulling not implemented')
)

#422
FIESTA_2201_PULLED_NOT_STRUCTURE = CommonStatusMessage(
    2201,
    _('Pulled not a structure SDMX message')
)

#423
FIESTA_2202_PULLED_NO_CONTENT_STRUCTURE = CommonStatusMessage(
    2202,
    _('Pulled a structure SDMX message with no content')
)

#424
FIESTA_2203_PULLED_UNEXPECTED_CONTENT = CommonStatusMessage(
    2203,
    _('Pulled a structure SDMX message with unexpected content')
)

#425
FIESTA_2303_NO_INLINE_STRUCTURE = CommonStatusMessage(
    2303,
    _('Inline not a structure SDMX message')
)

#431
FIESTA_2401_NOT_FOUND_PARENT = CommonStatusMessage(
    2401,
    _('Item parent not found')
)
#432
FIESTA_2402_REPRESENTATION_CODELIST_NOT_REGISTERED = CommonStatusMessage(
    2402,
    _('Cannot link represenation object to not registered codelist')
)

#433
FIESTA_2403_AGENCY_NOT_REGISTERED = CommonStatusMessage(
    2403,
    _('Maintainable artefact\'s agency not registered')
)

#441
FIESTA_2404_NO_EMAIL = CommonStatusMessage(
    2404,
    _('Contact not loaded since email is not provided')
)
FIESTA_2405_PARENT_NOT_IN_SCHEME = CommonStatusMessage(
    2405,
    _('Parent organisation does not belong to the child organisation scheme and will be ignored')
)
FIESTA_2501_NOT_SUPPORTED_LANGUAGE = CommonStatusMessage(
    2501,
    _('Message contains text in a not supported language')
)
