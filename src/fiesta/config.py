# flake8: noqa, because URL syntax is more readable with long lines

from django.apps import apps

from fiesta.core.application import BaseFiestaConfig

class FiestaConfig(BaseFiestaConfig):
    name = 'fiesta'

    def ready(self):
        self.common_app = apps.get_app_config('common')
        self.base_app = apps.get_app_config('base')
        self.codelist_app = apps.get_app_config('codelist')
        self.conceptscheme_app = apps.get_app_config('conceptscheme')
