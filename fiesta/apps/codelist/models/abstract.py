
from django.db import models

from fiesta.apps.common.models.abstract import ItemWithParent, MaintainableArtefact
from fiesta.settings import api_settings
from fiesta.core.validators import re_validators 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class AbstractCodelist(MaintainableArtefact):
    object_id = models.CharField('id', max_length=SMALL,
                                 validators=[re_validators['NCNameIDType']])

    class Meta(MaintainableArtefact.Meta):
        abstract = True


class AbstractCode(ItemWithParent):

    wrapper = models.ForeignKey('Codelist', verbose_name='Codelist',
                                on_delete=models.CASCADE, related_name='codes')

    class Meta(ItemWithParent.Meta):
        abstract = True
