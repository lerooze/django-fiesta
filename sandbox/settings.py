import os.path
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'treebeard',
    'rest_framework',
    # 'django_extensions',
    'versionfield',
    'multi_email_field',
    'fiesta',
    'fiesta.apps.registry',
    'fiesta.apps.common',
    'fiesta.apps.base',
    'fiesta.apps.codelist',
    'fiesta.apps.conceptscheme',
    'fiesta.apps.datastructure'
]
ROOT_URLCONF = 'urls'
DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sandbox', 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = 'base.User' 
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'fiesta.parsers.XMLParser21',
        'fiesta.parsers.XMLParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [        
        'fiesta.renderers.XMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ]
}

LANGUAGES = (
    ('en', _('English')),
    ('el', _('Greek'))
)

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/al459/media/' 
