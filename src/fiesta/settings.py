"""
Settings for FIESTA are all namespaced in the FIESTA setting.
For example your project's `settings.py` file might look like this:

FIESTA = {
    'DEFAULT_SENDER_ID': 'SDMXOPEN',
    'DEFAULT_STRING_LENGTH: 31 
}

This module provides the `api_setting` object, that is used to access
FIESTA settings, checking for user settings first, then falling
back to the defaults.
"""
import os.path
from importlib import import_module

from django.conf import settings
from django.test.signals import setting_changed

DEFAULTS = {
    'DEFAULT_SENDER_ID': 'FIESTA',
    'DEFAULT_TINY_STRING_LENGTH': 15, 
    'DEFAULT_VERY_SMALL_STRING_LENGTH': 31, 
    'DEFAULT_SMALL_STRING_LENGTH': 63, 
    'DEFAULT_STRING_LENGTH': 127, 
    'DEFAULT_LARGE_STRING_LENGTH': 255, 
    'DEFAULT_SCHEMA_PATH': os.path.join(os.path.expanduser('~'), 'schemas'),
    'DEFAULT_NEW_USER_PASSWORD': 'not_so_secret_password',
    'DEFAULT_SERIALIZER_MODULE': 'fiesta.core.serializers'
}

IMPORT_STRINGS = [
]

def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        module_path, class_name = val.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        class_name = e.__class__.__name__
        msg = f"Could not import '{val}' for API setting " \
              f"'{setting_name}'. {class_name}: {e}."
        raise ImportError(msg)

class APISettings:
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from fiesta.settings import api_settings
        print(api_settings.DEFAULT_SCHEMA_PATH)

    """
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'FIESTA', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid API setting: '{attr}'")

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        SETTINGS_DOC = "https://django-fiesta-readthedocs.io/en/stable/api/settings"
        for setting in DEFAULTS.REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    f"The '{setting}' setting of '{self._setting}' settings "
                    f"has been removed. Please refer to '{SETTINGS_DOC}' for "
                    f"available settings."
                )
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')

api_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)

def reload_api_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'FIESTA':
        api_settings.reload()

setting_changed.connect(reload_api_settings)
