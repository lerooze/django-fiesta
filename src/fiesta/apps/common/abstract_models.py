# abstract_models.py

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

from ...core import constants
from ...settings import api_settings 
from ...core.validators import re_validators, errors

from . import managers

VERY_SMALL = api_settings.DEFAULT_VERY_SMALL_STRING
MEDIUM = api_settings.DEFAULT_REGULAR_STRING
VERY_LARGE = api_settings.DEFAULT_VERY_LARGE_STRING

class SmallString(models.Model):
    text = models.CharField(
        max_length=MEDIUM,
        unique=True
    )

    class Meta:
        abstract = True

class LargeString(models.Model):
    text = models.CharField(
        max_length=VERY_LARGE,
        db_index=True
    )

    class Meta:
        abstract = True

class Annotation(models.Model):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        blank=True
    )
    annotation_title = models.CharField(
        _('title'), 
        max_length=MEDIUM,
        blank=True
    )
    annotation_type = models.CharField(
        _('type'), 
        max_length=VERY_SMALL, 
        blank=True
    )
    annotation_url = models.URLField(
        _('URL'), 
        blank=True
    )
    text = models.TextField(_('Text'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Annotation')
        verbose_name_plural = _('Annotations')

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.annotation_title, self.annotation_type)

class AbstractThrough(models.Model):
    name = models.ForeignKey(
        'common.MediumString',
        null=True,
        on_delete=models.CASCADE
    )
    description = models.ForeignKey(
        'common.LargeString',
        null=True,
        on_delete=models.CASCADE
    )
    annotation = models.ForeignKey(
        'common.Annotation',
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

class AbstractIdentifiable(models.Model):

    class Meta:
        abstract = True
        ordering = ['object_id']

    def __str__(self):
        return self.object_id 

class AbstractIdentifiable(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        ordering = ['object_id']
        abstract = True

class AbstractUIdentifiable(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        unique=True
    )

    class Meta:
        abstract = True

class AbstractNCNameIdentifiable(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractUNCNameIdentifiable(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        unique=True
    )

    class Meta:
        abstract = True

class AbstractNestedNCNameIdentifiable(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractUNestedNCNameIdentifiable(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        unique=True
    )

    class Meta:
        abstract = True

class AbstractIDItem(AbstractUIdentifiable):
    objects = managers.ItemManager()

    class Meta(AbstractUIdentifiable.meta):
        abstract = True

class AbstractNCNameIDItem(AbstractUNCNameIdentifiable):
    objects = managers.ItemManager()

    class Meta(AbstractUNCNameIdentifiable.meta):
        abstract = True

class AbstractNestedNCNameIDItem(AbstractUNestedNCNameIdentifiable):
    objects = managers.ItemManager()

    class Meta(AbstractUNestedNCNameIdentifiable.meta):
        abstract = True

class AbstractItemWithParent(MP_Node):

    objects = managers.ItemWithParentManager()

    class Meta:
        abstract = True

    def clean(self):
        parent = self.get_parent()
        if parent:
            if not self.containers.intersection(parent.wrappers):
                raise ValidationError({
                    'parent': errors['parent'],
                })

    def save(self, parent=None, **kwargs):
        if not self.depth:
            if parent:
                self.depth = parent.depth + 1
                parent.add_child(instance=self)
            else:
                self.add_root(instance=self)
            return  #add_root and add_child save as well
        super().save(**kwargs)

class AbstractIDItemWithParent(AbstractUIdentifiable, AbstractItemWithParent):

    class Meta(AbstractUIdentifiable.meta):
        abstract = True

class AbstractNCNameIDItemWithParent(AbstractUNCNameIdentifiable, AbstractItemWithParent):

    class Meta(AbstractUNCNameIdentifiable.meta):
        abstract = True

class AbstractNestedNCNameIDItemWithParent(AbstractUNestedNCNameIdentifiable, AbstractItemWithParent):

    class Meta(AbstractUNestedNCNameIdentifiable.meta):
        abstract = True

class AbstractMaintainable(models.Model):
    agency = models.ForeignKey(
        'base.Agency', 
        verbose_name=_('Agency'), 
        on_delete=models.PROTECT) 

    objects = managers.MaintainableManager() 

    class Meta:
        abstract = True
        ordering = ['agency', 'object_id']
        constraint = [
            models.UniqueConstraint(['object_id', 'agency'], 'unique')
        ]
        indexes = [
            models.Index(fields=['object_id','agency']),
        ]

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.agency)

class AbstractIDMaintainable(AbstractUIdentifiable, AbstractMaintainable):

    class Meta(AbstractMaintainable.meta):
        abstract = True

class AbstractNCNameIDMaintainable(AbstractUNCNameIdentifiable, AbstractMaintainable):

    class Meta(AbstractMaintainable.meta):
        abstract = True

class AbstractNestedNCNameIDMaintainable(AbstractUNestedNCNameIdentifiable, AbstractMaintainable):

    class Meta(AbstractMaintainable.meta):
        abstract = True

class AbstractVersionable(models.Model):
    major = models.IntegerField(default=1, db_index=True)
    minor = models.IntegerField(default=0, db_index=True)
    patch = models.IntegerField(null=True, db_index=True)
    valid_from = models.DateTimeField(
        _('Valid from'),
        null=True,
        blank=True)
    valid_to = models.DateTimeField(
        _('Valid to'),
        null=True,
        blank=True)
    is_final = models.BooleanField(
        _('Is final'), 
        default=False)
    submitted_structure = models.ManyToManyField('registry.SubmittedStructure')

    class Meta:
        abstract = True
        ordering = ['-major', '-minor', '-patch']
        indexes = [
            models.Index(fields=['-major', '-minor', '-patch']),
            models.Index(fields=['-minor', '-patch']),
        ]
        verbose_name = _('Versionable')
        verbose_name_plural = _('Versionables')

class Format(models.Model):
    text_type = models.CharField(
        _('Text type'),
        max_length=VERY_SMALL, 
        choices=constants.DATA_TYPES,
        null=True, blank=True
    )
    is_sequence = models.NullBooleanField(
        _('Is sequence'), 
        null=True, 
        blank=True)
    interval = models.DecimalField(
        _('Interval'),
        null=True, 
        blank=True,
        max_digits=19, 
        decimal_places=10)
    start_value = models.DecimalField(
        _('Start value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10)
    end_value = models.DecimalField(
        _('End value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10)
    time_interval = models.DurationField(
        _('Time interval'),
        null=True, 
        blank=True)
    start_time = models.DateTimeField(
        _('Start time'),
        null=True, 
        blank=True)
    end_time = models.DateTimeField(
        _('End time'),
        null=True, blank=True)
    min_length = models.PositiveIntegerField(
        _('Minimum length'),
        null=True, 
        blank=True)
    max_length = models.PositiveIntegerField(
        _('Maximum length'), 
        null=True, 
        blank=True)
    min_value= models.DecimalField(
        _('Minimum value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10)
    max_value = models.DecimalField(
        _('Maximum value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10)
    decimals = models.PositiveIntegerField(
        _('Decimals'),
        null=True, 
        blank=True)
    pattern = models.TextField(
        _('Pattern'),
        null=True, 
        blank=True)
    is_multi_lingual = models.BooleanField(
        _('Is multi lingual'),
        null=True, 
        blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')

class Representation(models.Model):

    text_format = models.ForeignKey(
        'common.Format', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='+', 
        verbose_name=_('Text format'))
    enumeration = models.ForeignKey(
        'codelist.Codelist', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name=_('Enumeration')
    )
    enumeration_format = models.ForeignKey(
        'common.Format', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='+',
        verbose_name=_('Enumeration format')
    )

    class Meta:
        abstract = True
        verbose_name = _('Representation')
        verbose_name_plural = _('Representations')

# class AbstractComponent(AbstractIdentifiable):
#
#     object_id = models.CharField(
#         _('ID'), 
#         max_length=SMALL, 
#         validators=[re_validators['NCNameIDType']],
#         blank=True,
#         db_index=True
#     )
#
#     class Meta:
#         abstract = True
#         unique_together = ('object_id', 'concept_identity', 'wrapper')
#         indexes = [
#             models.Index(fields=['concept_identity']),
#             models.Index(fields=['object_id', 'concept_identity']),
#             models.Index(fields=['object_id', 'wrapper']),
#             models.Index(fields=['concept_identity', 'wrapper']),
#             models.Index(fields=['object_id', 'concept_identity', 'wrapper']),
#         ]
#
# class ReferencePeriod(models.Model):
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
