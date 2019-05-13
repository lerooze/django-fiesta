"""
Settings for DJANGO_SDMX are all namespaced in the DJANGO_SDMX setting.
For example your project's `settings.py` file might look like this:

DJANGO_SDMX = {
    'DEFAULT_LENGTHS': {
        'id_code': 64,
        'name': 128
    },
}

This module provides the `api_setting` object, that is used to access
DJANGO_SDMX settings, checking for user settings first, then falling
back to the defaults.
"""
import os.path

from django.conf import settings
from django.test.signals import setting_changed

from .utils.loaders import load_yaml, load_error_descriptions


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = load_yaml(os.path.join(MODULE_DIR, 'conf', 'default_settings.yaml'))
ERROR_DESCRIPTIONS = load_error_descriptions(os.path.join(MODULE_DIR, 'conf', 'error_descriptions.yaml'))
DEFAULTS.FIESTA['MODULE_DIR'] = MODULE_DIR
DEFAULTS.FIESTA['ERROR_DESCRIPTIONS'] = ERROR_DESCRIPTIONS 
DEFAULTS.FIESTA['SCHEMAS'] = os.path.join(MODULE_DIR, 'conf', 'schema')

class APISettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from hydro_sdmx.settings import api_settings
        print(api_settings.DEFAULT_CHARVAR_LENGTHS)

    """
    def __init__(self, setting, user_settings=None, defaults=None):
        self._setting = self.__check_setting(setting)
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS[setting]

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, self._setting, {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid %s setting: '%s'" % (self._setting, attr))

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val

    def __check_setting(self, setting):
        if setting not in ['FIESTA', 'FIESTA_MAXLENGTHS']:
            raise RuntimeError("The '%s' global setting is not allowed.  Please choose one of the following '%s'" % (setting, ['FIESTA', 'FIESTA_MAXLENGTHS']))
        return setting

    def __check_user_settings(self, user_settings):
        SETTINGS_DOC = "https://django-SDMX-readthedocs.io/en/stable/api/settings"
        for setting in DEFAULTS.REMOVED_SETTINGS[self._setting]:
            if setting in user_settings:
                raise RuntimeError("The '%s' setting of '%s' settings has been removed. Please refer to '%s' for available settings." % (setting, self._setting, SETTINGS_DOC))
        return user_settings

api_settings = APISettings('FIESTA', None, DEFAULTS.FIESTA)
api_maxlen_settings = APISettings('FIESTA_MAXLENGTHS', None,
                                  DEFAULTS.FIESTA_MAXLENGTHS)

def reload_api_settings(*args, **kwargs):
    global api_settings
    global api_maxlen_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'FIESTA':
        api_settings = APISettings(setting, value, DEFAULTS[setting])
    elif setting == 'FIESTA_MAXLENGTHS':
        api_maxlen_settings = APISettings(setting, value, DEFAULTS[setting])

setting_changed.connect(reload_api_settings)
