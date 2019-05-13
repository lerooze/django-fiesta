from django.db import models

from .abstract import ItemWithParent, MaintainableArtefact
from .common import Representation

from ..settings import api_maxlen_settings as max_length
from ..validators import re_validators

class ConceptScheme(MaintainableArtefact):
    object_id = models.CharField(
        'id', max_length=max_length.OBJECT_ID,
        validators=[re_validators['NCNameIDType']],
    )

class ISOConceptReference(models.Model):
    concept_agency = models.CharField(max_length=max_length.NAME)
    concept_scheme_id = models.CharField(max_length=max_length.OBJECT_ID)
    concept_id = models.CharField(max_length=max_length.OBJECT_ID)

class Concept(ItemWithParent):
    object_id = models.CharField(
        'id', max_length=max_length.OBJECT_ID,
        validators=[re_validators['IDType']],
    )
    wrapper = models.ForeignKey(ConceptScheme, on_delete=models.CASCADE,
                                related_name='concepts')
    core_representation = models.ForeignKey(Representation, on_delete=models.CASCADE)
    iso_concept_reference = models.ForeignKey(ISOConceptReference, null=True,
                                              blank=True,
                                              on_delete=models.CASCADE,
                                              related_name='concepts')
