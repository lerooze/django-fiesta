from django.db import models

from .abstract import ItemWithParent, MaintainableArtefact

from ..settings import api_maxlen_settings as max_length
from ..validators import re_validators 


#Concrete models
class Codelist(MaintainableArtefact):
    object_id = models.CharField('id', max_length=max_length.OBJECT_ID,
                               validators=[re_validators['NCNameIDType']])

class Code(ItemWithParent):
    wrapper = models.ForeignKey(Codelist, verbose_name='Codelist',
                                on_delete=models.CASCADE)
