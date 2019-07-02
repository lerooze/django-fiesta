import os
import sys

import django
from django.core import management


def pytest_addoption(parser):
    parser.addoption('--no-pkgroot', action='store_true', default=False,
                     help='Remove package root directory from sys.path, ensuring that '
                          'fiesta is imported from the installed site-packages. '
                          'Used for testing the distribution.')
    parser.addoption('--staticfiles', action='store_true', default=False,
                     help='Run tests with static files collection, using manifest '
                          'staticfiles storage. Used for testing the distribution.')


def pytest_configure(config):
    from django.conf import settings

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

    if config.getoption('--no-pkgroot'):
        sys.path.pop(0)

        # import rest_framework before pytest re-adds the package root directory.
        import fiesta 
        package_dir = os.path.join(os.getcwd(), 'fiesta')
        assert not fiesta.__file__.startswith(package_dir)

    # Manifest storage will raise an exception if static files are not present (ie, a packaging failure).
    if config.getoption('--staticfiles'):
        import fiesta 
        settings.STATIC_ROOT = os.path.join(os.path.dirname(fiesta.__file__), 'static-root')
        settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

    django.setup()

    if config.getoption('--staticfiles'):
        management.call_command('collectstatic', verbosity=0, interactive=False)
