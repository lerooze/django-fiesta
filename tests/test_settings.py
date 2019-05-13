import os.path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'fiesta',
]
ROOT_URLCONF = 'tests.urls'
DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]
TEMPLATES=[{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'fiesta.parsers.XMLParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'fiesta.renderers.XMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
