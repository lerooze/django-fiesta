import re

from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator, ValidationError

errors = {
    'parent': ValidationError(
        _('Parent and child objects must be  wrapped by the same object'),
        code='local'
    ),
}
patterns = {
    'NestedIDType': "[A-Za-z0-9_@$\-]+(\.[A-Za-z0-9_@$\-]+)*",
    'TwoLevelIDType': "[A-Za-z0-9_@$\-]+\.[A-Za-z0-9_@$\-]+",
    'IDType': "^[A-Za-z0-9_@$\-]+$",
    'NCNameIDType': "[A-Za-z][A-Za-z0-9_\-]*",
    'NestedNCNameIDType': "[A-Za-z][A-Za-z0-9_\-]*(\.[A-Za-z][A-Za-z0-9_\-]*)*",
    'SingleNCNameIDType': "[A-Za-z][A-Za-z0-9_\-]*",
    'VersionType': "[0-9]+(\.[0-9]+)*",
}

re_validators = {
    key: RegexValidator(
            re.compile(value), 
            _('Enter a value of type %s that has pattern "(%s)"') % 
                (key, value), 
            'invalid_pattern'
         ) 
    for key, value in patterns.items()
}

clean_validators = {
    'MaintainableArtefact': {
        'update' : ValidationError(
            _('Final structures cannot be updated'),
            'isfinal',
        ),
        'contact': ValidationError(
            _('A user that is not a contact cannot modify structures'),
            'notcontact'
        )
    },
    'Obs': ValidationError(
        _('Obs instances cannot be modified.  Create a new instance and select the appropriate action'),
        'exists'
    )
}
