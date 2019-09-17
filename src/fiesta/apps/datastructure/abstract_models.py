# abstract_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings
from ...core import constants

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH


class AbstractDataStructure(common.MaintainableArtefact):

    class Meta(common.MaintainableArtefact.Meta):
        abstract = True

class ComponentList(common.AnnotableArtefact):

    data_structure = models.OneToOneField(
        'DataStructure', on_delete=models.CASCADE)

    class Meta(common.AnnotableArtefact.Meta):
        abstract = True

class AbstractDimensionList(ComponentList):

    class Meta(ComponentList.Meta):
        abstract = True

class AbstractGroup(common.IdentifiableArtefact):

    data_structure = models.ForeignKey('DataStructure', on_delete=models.CASCADE)

    class Meta(common.IdentifiableArtefact.Meta):
        abstract = True
        unique_together = ('object_id', 'data_structure')
        indexes = [
            models.Index(fields=['object_id']),
            models.Index(fields=['data_structure']),
            models.Index(fields=['object_id', 'data_structure']),
        ]

class AbstractAttributeList(ComponentList):

    class Meta(ComponentList.Meta):
        abstract = True

class AbstractMeasureList(ComponentList):

    class Meta(ComponentList.Meta):
        abstract = True

class AbstractDimension(common.Component):

    wrapper = models.ForeignKey(
        'DimensionList', on_delete=models.CASCADE)
    concept_identity = models.ForeignKey(
        'conceptscheme.Concept', on_delete=models.CASCADE,
        related_name='dimension_concept_identity_set',
        related_query_name='dimension_concept_identity')
    local_representation = models.ForeignKey(
        'common.Representation', on_delete=models.CASCADE)
    measure_local_representation = models.ForeignKey(
        'conceptscheme.ConceptScheme', on_delete=models.CASCADE)
    concept_role = models.ManyToManyField(
        'conceptscheme.Concept', related_name='dimension_concept_role_set',
        related_query_name='dimension_concept_role')
    position = models.IntegerField(_('position'))
    tipe = models.CharField(_('type'), max_length=SMALL, choices=constants.DIMENSION_TYPES)

    class Meta(common.Component.Meta):
        abstract = True

class AbstractGroupDimension(common.AnnotableArtefact):

    wrapper = models.ForeignKey(
        'Group', on_delete=models.CASCADE)
    dimension_reference = models.ForeignKey('Dimension', on_delete=models.CASCADE)

    class Meta(common.AnnotableArtefact.Meta):
        abstract = True
        unique_together = ('wrapper', 'dimension_reference')
        indexes = [
            models.Index(fields=['wrapper']),
            models.Index(fields=['dimension_reference']),
            models.Index(fields=['wrapper', 'dimension_reference']),
        ]

class AbstractPrimaryMeasure(common.Component):

    wrapper = models.ForeignKey(
        'PrimaryMeasure', on_delete=models.CASCADE)
    concept_identity = models.ForeignKey(
        'conceptscheme.Concept', on_delete=models.CASCADE)
    local_representation = models.ForeignKey(
        'common.Representation', on_delete=models.CASCADE)

    class Meta(common.Component.Meta):
        abstract = True

class AbstractAttribute(common.Component):

    wrapper = models.ForeignKey(
        'AttributeList', on_delete=models.CASCADE)
    concept_identity = models.ForeignKey(
        'conceptscheme.Concept', on_delete=models.CASCADE,
        related_name='attribute_concept_identity_set',
        related_query_name='attribute_concept_identity')
    local_representation = models.ForeignKey(
        'common.Representation', on_delete=models.CASCADE)
    concept_role = models.ManyToManyField(
        'conceptscheme.Concept', related_name='attribute_concept_role_set',
        related_query_name='attribute_concept_role')
    assignment_status = models.CharField(
        max_length=SMALL, choices=constants.ASSIGNMENT_STATUS)

    class Meta(common.Component.Meta):
        abstract = True

class AbstractAttributeRelationship(models.Model):
    attribute = models.OneToOneField('Attribute', on_delete=models.CASCADE)
    null = models.BooleanField(default=False)
    dimension = models.ManyToManyField('Dimension', related_name='+')
    attachment_group = models.ManyToManyField('Group', related_name='+')
    group = models.ForeignKey(
        'Group', on_delete=models.CASCADE, related_name='+')
    primary_measure = models.BooleanField(default=False)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['attribute']),
        ]

class AbstractDataflow(common.MaintainableArtefact):
    structure = models.ForeignKey('DataStructure', on_delete=models.CASCADE)

    class Meta:
        abstract = True
