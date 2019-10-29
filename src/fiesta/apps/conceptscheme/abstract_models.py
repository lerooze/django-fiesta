# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING

class Annotation(common.AbstractAnnotation):
    concept_scheme = models.ForeignKey(
        'conceptscheme.ConceptScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Concept scheme'),
        null=True,
        blank=True,
    )
    concept = models.ForeignKey(
        'conceptscheme.Concept',
        on_delete=models.CASCADE,
        verbose_name=_('Concept'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

class ConceptScheme(common.AbstractNCNameMaintainable):

    class Meta(common.AbstractNCNameMaintainable.Meta):
        abstract = True
        verbose_name = _('Concept scheme')
        verbose_name_plural = _('Concept schemes')

class Concept(common.AbstractNCNameItemWithParent):
    container = models.ForeignKey(
        'ConceptScheme', 
        on_delete=models.CASCADE,
        verbose_name=_('Concept scheme')
    )
    core_representation = models.ForeignKey(
        'common.Representation', 
        on_delete=models.PROTECT,
        verbose_name=_('Core representation'),
        null=True,
        blank=True
    )
    iso_concept_reference = models.ForeignKey(
        'conceptscheme.ISOConceptReference', 
        null=True, 
        blank=True, 
        on_delete=models.PROTECT,
        verbose_name=_('ISO concept')
    )

    class Meta(common.AbstractNCNameItemWithParent.Meta):
        abstract = True

class ISOConceptReference(models.Model):
    concept_agency = models.CharField(
        _('Concept agency'),
        max_length=SMALL
    )
    concept_scheme_id = models.CharField(
        _('Concept scheme ID'),
        max_length=SMALL
    )
    concept_id = models.CharField(
        _('Concept ID'),
        max_length=SMALL
    )

    class Meta:
        abstract = True
