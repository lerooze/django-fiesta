# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..common import abstract_models as common 

class Annotation(common.Annotation):
    codelist = models.ForeignKey(
        'codelist.Codelist',
        on_delete=models.CASCADE,
        verbose_name=_('Codelist'),
        null=True,
        blank=True,
    )
    code = models.ForeignKey(
        'codelist.Code',
        on_delete=models.CASCADE,
        verbose_name=_('Code'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

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
        on_delete=models.CASCADE,
        verbose_name=_('Codelist')
    )

    class Meta(common.AbstractItemWithParent.Meta):
        abstract = True
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')
