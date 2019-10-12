# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class AbstractBaseReference(models.Model):
    codelist_set = models.ManyToManyField('codelist.Codelist')
    code_set = models.ManyToManyField('codelist.Code')

    class Meta:
        abstract = True

class Text(AbstractBaseReference, common.AbstractText):
    pass

class Annotation(AbstractBaseReference, common.AbstractAnnotation):
    pass

class Versionable(common.AbstractVersionable):
    codelist = models.ForeignKey(
        'codelist.Codelist',
        verbose_name=_('Codelist')
    )

    class Meta(common.AbstractVersionable.Meta):
        abstract = True

class Codelist(common.AbstractMaintainable):
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True,
    )

    class Meta(common.MaintainableArtefact.Meta):
        abstract = True
        verbose_name = _('Codelist')
        verbose_name_plural = _('Codelists')

class Code(common.ItemWithParent):

    containers = models.ManyToManyField(
        'codelist.Versionable',
        verbose_name=_('Containers'))

    class Meta(common.ItemWithParent.Meta):
        abstract = True
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')
