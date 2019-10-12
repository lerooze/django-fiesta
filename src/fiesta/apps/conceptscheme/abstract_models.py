# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class Versionable(common.AbstractVersionable):
    conceptscheme = models.ForeignKey(
        'conceptscheme.ConceptScheme',
        verbose_name=_('Concept scheme')
    )

    class Meta(common.AbstractVersionable.Meta):
        abstract = True

class AbstractBaseReference(models.Model):
    versionable_set = models.ManyToManyField('conceptscheme.Versionable')
    concept_set = models.ManyToManyField('conceptscheme.Concept')

    class Meta:
        abstract = True

class Text(AbstractBaseReference, common.AbstractText):
    pass

class Annotation(AbstractBaseReference, common.AbstractAnnotation):
    pass


class ConceptScheme(common.AbstractMaintainable):
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True)

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Concept scheme')
        verbose_name_plural = _('Concept schemes')

class Concept(common.AbstractItemWithParent):
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL,
        validators=[re_validators['NCNameIDType']],
        unique=True)
    wrapper = models.ForeignKey('ConceptScheme', on_delete=models.CASCADE)
    core_representation = models.ForeignKey('common.Representation',
                                            on_delete=models.CASCADE)
    iso_concept_reference = models.ForeignKey('ISOConceptReference', null=True,
                                              blank=True,
                                              on_delete=models.CASCADE)

    class Meta:
        abstract = True

class AbstractISOConceptReference(models.Model):
    concept_agency = models.CharField(max_length=SMALL)
    concept_scheme_id = models.CharField(max_length=SMALL)
    concept_id = models.CharField(max_length=SMALL)

    class Meta:
        abstract = True

