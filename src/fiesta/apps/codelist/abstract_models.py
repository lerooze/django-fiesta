# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class AbstractCodelist(common.MaintainableArtefact):
    object_id = models.CharField('id', max_length=SMALL,
                                 validators=[re_validators['NCNameIDType']])

    class Meta(common.MaintainableArtefact.Meta):
        abstract = True
        app_label = 'codelist'
        verbose_name = _('Codelist')
        verbose_name_plural = _('Codelists')

class AbstractCode(common.ItemWithParent):

    wrapper = models.ForeignKey('Codelist', verbose_name='Codelist', on_delete=models.CASCADE)

    class Meta(common.ItemWithParent.Meta):
        abstract = True
        app_label = 'codelist'
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')
