# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from versionfield import VersionField

from ...settings import api_settings
from ..common import abstract_models as common

TINY = api_settings.DEFAULT_TINY_STRING

class Annotation(common.AbstractAnnotation):
    data_structure = models.ForeignKey(
        'datastructure.DataStructure',
        on_delete=models.CASCADE,
        verbose_name=_('Data structure'),
        null=True,
        blank=True,
    )
    dimension_list = models.ForeignKey(
        'datastructure.DimensionList',
        on_delete=models.CASCADE,
        verbose_name=_('Dimension list'),
        null=True,
        blank=True,
    )
    group = models.ForeignKey(
        'datastructure.Group',
        on_delete=models.CASCADE,
        verbose_name=_('Group'),
        null=True,
        blank=True,
    )
    attribute_list = models.ForeignKey(
        'datastructure.AttributeList',
        on_delete=models.CASCADE,
        verbose_name=_('Attribute list'),
        null=True,
        blank=True,
    )
    measure_list = models.ForeignKey(
        'datastructure.MeasureList',
        on_delete=models.CASCADE,
        verbose_name=_('Measure list'),
        null=True,
        blank=True,
    )
    dimension = models.ForeignKey(
        'datastructure.Dimension',
        on_delete=models.CASCADE,
        verbose_name=_('Dimension'),
        null=True,
        blank=True,
    )
    group_dimension = models.ForeignKey(
        'datastructure.GroupDimension',
        on_delete=models.CASCADE,
        verbose_name=_('Group dimension'),
        null=True,
        blank=True,
    )
    primary_measure = models.ForeignKey(
        'datastructure.PrimaryMeasure',
        on_delete=models.CASCADE,
        verbose_name=_('Primary measure'),
        null=True,
        blank=True,
    )
    attribute = models.ForeignKey(
        'datastructure.Attribute',
        on_delete=models.CASCADE,
        verbose_name=_('Attribute'),
        null=True,
        blank=True,
    )
    dataflow = models.ForeignKey(
        'datastructure.Dataflow',
        on_delete=models.CASCADE,
        verbose_name=_('Dataflow'),
        null=True,
        blank=True,
    )
    class Meta:
        abstract = True

class DataStructure(common.AbstractMaintainable):

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True

class AbstractComponentList(models.Model):

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
        'registry.AttachmentConstraint', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_('Attachment constraint')
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
    class Type(models.IntegerChoices):
        DIMENSION = 0, _('Dimension')
        TIME_DIMENSION = 1, _('Time dimension')
        MEASURE_DIMENSION = 2, _('Measure dimension')

    container = models.ForeignKey(
        'DimensionList', 
        on_delete=models.CASCADE
    )
    concept_identity = models.ForeignKey(
        'conceptscheme.Concept',
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
        'conceptscheme.ConceptScheme', 
        on_delete=models.PROTECT,
        verbose_name=_('Measure local representation')
    )
    local_representation_version = VersionField(
        _('Measure local representation version'),
        blank=True,
        null=True
    )
    concept_role = models.ManyToManyField(
        'conceptscheme.Concept', 
        related_name='dimension_conceptrole_set',
        related_query_name='dimension_conceptrole',
        verbose_name=_('Concept roles')
    )
    position = models.IntegerField(_('position'))
    tipe = models.IntegerField(
        _('type'), 
        choices=Type.choices,
        default=Type.DIMENSION
    )

    class Meta(common.AbstractComponent.Meta):
        abstract = True
        verbose_name = 'Dimension'
        verbose_name_plural = 'Dimensions'

class GroupDimension(models.Model):

    container = models.ForeignKey(
        'Group', 
        on_delete=models.CASCADE,
        verbose_name=_('Group')
    )
    dimension = models.ForeignKey(
        'Dimension', 
        on_delete=models.CASCADE,
        verbose_name=_('Dimension')
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['container', 'dimension'],
                name='unique_group_dimension'
            )
        ]
        indexes = [
            models.Index(fields=['container', 'dimension']),
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
        'conceptscheme.Concept',
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


    class AssignmentStatus(models.IntegerChoices):
        MANDATORY = 0, _('Mandatory')
        CONDITIONAL = 1, _('Conditional')
        

    container = models.ForeignKey(
        'AttributeList', 
        on_delete=models.CASCADE,
        verbose_name=_('Attribute list')
    )
    concept_identity = models.ForeignKey(
        'conceptscheme.Concept',
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
        'conceptscheme.Concept', 
        related_name='attribute_concept_role_set',
        related_query_name='attribute_concept_role',
        verbose_name=_('Concept roles')
    )
    assignment_status = models.IntegerField(
        _('Assignment status'),
        choices=AssignmentStatus.choices
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
    primary_measure = models.ManyToManyField(
        'PrimaryMeasure', 
        related_name='+',
        verbose_name=_('Primary measures')
    )

    class Meta:
        abstract = True

class Dataflow(common.AbstractMaintainable):
    structure = models.ForeignKey(
        'DataStructure', 
        on_delete=models.PROTECT,
        verbose_name=_('Data structure reference')
    )

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Dataflow')
        verbose_name_plural = _('Dataflows')
