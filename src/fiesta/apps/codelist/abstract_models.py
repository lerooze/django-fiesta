# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings

from ..common import abstract_models as common 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class CodelistReference(common.AbstractReference):

    class Meta:
        abstract = True
        verbose_name = _('Codelist reference')
        verbose_name_plural = _('Codelist references')

class Codelist(common.AbstractNCNameMaintainable):

    class Meta(common.AbstractNCNameMaintainable.Meta):
        abstract = True
        verbose_name = _('Codelist')
        verbose_name_plural = _('Codelists')

class Code(common.AbstractItemWithParent):

    container = models.ForeignKey(
        'codelist.Codelist',
        verbose_name=_('Codelist')
    )

    class Meta(common.ItemWithParent.Meta):
        abstract = True
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')
