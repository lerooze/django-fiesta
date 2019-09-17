# abstract_models.py

from django.db import models

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class AbstractConceptScheme(common.MaintainableArtefact):
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

class AbstractConcept(common.ItemWithParent):
    object_id = models.CharField('id', max_length=SMALL,
                                 validators=[re_validators['IDType']],)
    wrapper = models.ForeignKey('ConceptScheme', on_delete=models.CASCADE)
    core_representation = models.ForeignKey('common.Representation',
                                            on_delete=models.CASCADE)
    iso_concept_reference = models.ForeignKey('ISOConceptReference', null=True,
                                              blank=True,
                                              on_delete=models.CASCADE)

    class Meta:
        abstract = True
