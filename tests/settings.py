
from django.utils.translation import gettext_lazy as _

DEBUG_PROPAGATE_EXCEPTIONS = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
SITE_ID = 1
SECRET_KEY = 'not very secret in tests'
USE_I18N = True
USE_L10N = True
STATIC_URL = '/static/'
ROOT_URLCONF = 'tests._site.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            "debug": True,  # We want template errors to raise
        }
    },
]
AUTH_USER_MODEL = 'base.user'
MIDDLEWARE = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'treebeard',
    'rest_framework',
    'versionfield',
    'multi_email_field',
    'fiesta',
    'fiesta.apps.registry',
    'fiesta.apps.common',
    'fiesta.apps.base',
    'fiesta.apps.codelist',
    'fiesta.apps.conceptscheme',
    'fiesta.apps.datastructure',
]
LANGUAGES = (
    ('en', _('English')),
    ('el', _('Greek'))
)
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'fiesta.parsers.XMLParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'fiesta.renderers.XMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
# # guardian is optional
# try:
#     import guardian  # NOQA
# except ImportError:
#     pass
# else:
#     settings.ANONYMOUS_USER_ID = -1
#     settings.AUTHENTICATION_BACKENDS = (
#         'django.contrib.auth.backends.ModelBackend',
#         'guardian.backends.ObjectPermissionBackend',
#     )
#     settings.INSTALLED_APPS += (
#         'guardian',
#     )
