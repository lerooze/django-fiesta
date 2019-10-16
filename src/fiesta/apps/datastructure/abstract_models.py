# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from ...settings import api_settings
from ..common import abstract_models as common

TINY = api_settings.DEFAULT_TINY_STRING

class DataStructureReference(common.AbstractReference):
    class Meta:
        abstract = True
        verbose_name = _('Data structure reference')
        verbose_name_plural = _('Data structure references')

class DataStructure(common.AbstractMaintainable):
    content_constraint = models.ForeignKey(
        'registry.ContentConstraintReference',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Content constraint reference')
    )

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True

class AbstractComponentList(common.AbstractAnnotable):

    data_structure = models.OneToOneField(
        'DataStructure', 
        on_delete=models.PROTECT,
        verbose_name=_('Data structure')
    )

    class Meta:
        abstract = True

class DimensionList(AbstractComponentList):

    class Meta:
        abstract = True

class Group(common.AbstractIdentifiable):

    data_structure = models.ForeignKey(
        'DataStructure', 
        on_delete=models.CASCADE,
        verbose_name=_('Data structure')
    )
    attachment_constraint = models.ForeignKey(
        'registry.AttachmentConstraintReference', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_('Attachment constraint reference')
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['data_structure', 'object_id'],
                name='unique_group'
            )
        ]
        indexes = [
            models.Index(fields=['data_structure', 'object_id']),
        ]
        ordering = ['data_structure', 'object_id']

class AttributeList(AbstractComponentList):

    class Meta:
        abstract = True

class MeasureList(AbstractComponentList):

    class Meta:
        abstract = True

class Dimension(common.AbstractComponent):
    TYPE_CHOICES = Choices( 
        (0, 'DIMENSION', 'Dimension'),
        (1, 'TIME_DIMENSION', 'TimeDimension'),
        (2, 'MEASURE_DIMENSION', 'MeasureDimension')
    )
    container = models.ForeignKey(
        'DimensionList', 
        on_delete=models.CASCADE
    )
    concept_identity = models.ForeignKey(
        'conceptscheme.ConceptReference',
        on_delete=models.PROTECT,
        related_name='dimension_concept_identity_set',
        related_query_name='dimension_concept_identity',
        verbose_name=_('Concept identity')
    )
    local_representation = models.ForeignKey(
        'common.Representation', 
        on_delete=models.PROTECT,
        verbose_name=_('Local represenation')
    )
    measure_local_representation = models.ForeignKey(
        'conceptscheme.ConceptSchemeReference', 
        on_delete=models.PROTECT,
        verbose_name=_('Local representation')
    )
    concept_role = models.ManyToManyField(
        'conceptscheme.ConceptReference', 
        related_name='dimension_concept_role_set',
        related_query_name='dimension_concept_role',
        verbose_name=_('Concept roles')
    )
    position = models.IntegerField(_('position'))
    tipe = models.IntegerField(
        _('type'), 
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES.DIMENSION
    )

    class Meta(common.AbstractComponent.Meta):
        abstract = True
        verbose_name = 'Dimension'
        verbose_name_plural = 'Dimensions'

class GroupDimension(common.AbstractAnnotable):

    container = models.ForeignKey(
        'Group', 
        on_delete=models.CASCADE,
        verbose_name=_('Group')
    )
    dimension_reference = models.ForeignKey(
        'Dimension', 
        on_delete=models.CASCADE,
        verbose_name=_('Dimension')
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['container', 'dimension_reference'],
                name='unique_group_dimension'
            )
        ]
        indexes = [
            models.Index(fields=['container', 'dimension_reference']),
        ]
        verbose_name = _('Group dimension')
        verbose_name_plural = _('Group dimensions')

class PrimaryMeasure(common.AbstractComponent):

    container = models.ForeignKey(
        'MeasureList', 
        on_delete=models.CASCADE,
        verbose_name=_('Measure list')
    )
    concept_identity = models.ForeignKey(
        'conceptscheme.ConceptReference',
        on_delete=models.PROTECT,
        verbose_name=_('Concept identity')
    )
    local_representation = models.ForeignKey(
        'common.Representation', 
        on_delete=models.PROTECT,
        verbose_name=_('Local representation')
    )

    class Meta(common.AbstractComponent.Meta):
        abstract = True
        verbose_name = _('Primary measure')
        verbose_name_plural = _('Primary measures')

class Attribute(common.AbstractComponent):
    ASSIGNMENT_STATUS_CHOICES = Choices(
        (0, 'MANDATORY', 'Mandatory'),
        (1, 'CONDITIONAL', 'Conditional')
    )
    container = models.ForeignKey(
        'AttributeList', 
        on_delete=models.CASCADE,
        verbose_name=_('Attribute list')
    )
    concept_identity = models.ForeignKey(
        'conceptscheme.ConceptReference',
        on_delete=models.PROTECT,
        related_name='attribute_concept_identity_set',
        related_query_name='attribute_concept_identity',
        verbose_name=_('Concept identity')
    )
    local_representation = models.ForeignKey(
        'common.Representation', 
        on_delete=models.PROTECT,
        verbose_name=_('Local represenation')
    )
    concept_role = models.ManyToManyField(
        'conceptscheme.ConceptReference', 
        related_name='attribute_concept_role_set',
        related_query_name='attribute_concept_role',
        verbose_name=_('Concept roles')
    )
    assignment_status = models.IntegerField(
        _('Assignment status'),
        choices=ASSIGNMENT_STATUS_CHOICES
    )

    class Meta(common.AbstractComponent.Meta):
        abstract = True
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'

class AttributeRelationship(models.Model):
    attribute = models.OneToOneField(
        'Attribute', 
        on_delete=models.CASCADE,
        verbose_name=_('Attribute')
    )
    null = models.BooleanField(
        _('Null'), 
        default=False
    )
    dimension = models.ManyToManyField(
        'Dimension', 
        related_name='+',
        verbose_name=_('Dimensions')
    )
    attachment_group = models.ManyToManyField(
        'Group', 
        related_name='+',
        verbose_name=_('Groups')
    )
    group = models.ForeignKey(
        'Group', 
        on_delete=models.CASCADE, 
        related_name='+',
        verbose_name=_('Group')
    )
    primary_measure = models.BooleanField(
        _('Primary measure'),
        default=False
    )

    class Meta:
        abstract = True

class DataflowReference(common.AbstractReference):
    class Meta:
        abstract = True
        verbose_name = _('Dataflow reference')
        verbose_name_plural = _('Dataflow references')

class Dataflow(common.AbstractMaintainable):
    content_constraint = models.ForeignKey(
        'registry.ContentConstraintReference',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Content constraint reference')
    )
    structure = models.ForeignKey(
        'DataStructureReference', 
        on_delete=models.PROTECT,
        verbose_name=_('Data structure reference')
    )

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Dataflow')
        verbose_name_plural = _('Dataflows')
