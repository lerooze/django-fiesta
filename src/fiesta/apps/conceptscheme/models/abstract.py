
from django.db import models

from fiesta.apps.common.models.abstract import ItemWithParent, MaintainableArtefact
from fiesta.settings import api_settings
from fiesta.core.validators import re_validators 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class AbstractConceptScheme(MaintainableArtefact):
    object_id = models.CharField('id', max_length=SMALL,
                                 validators=[re_validators['NCNameIDType']],)

    class Meta:
        abstract = True

class AbstractISOConceptReference(models.Model):
    concept_agency = models.CharField(max_length=SMALL)
    concept_scheme_id = models.CharField(max_length=SMALL)
    concept_id = models.CharField(max_length=SMALL)

    class Meta:
        abstract = True

class AbstractConcept(ItemWithParent):
    object_id = models.CharField('id', max_length=SMALL,
                                 validators=[re_validators['IDType']],)
    wrapper = models.ForeignKey('ConceptScheme', on_delete=models.CASCADE,
                                related_name='concepts')
    core_representation = models.ForeignKey('common.Representation',
                                            on_delete=models.CASCADE,
                                            related_name='concepts')
    iso_concept_reference = models.ForeignKey('ISOConceptReference', null=True,
                                              blank=True,
                                              on_delete=models.CASCADE,
                                              related_name='concepts')

    class Meta:
        abstract = True
