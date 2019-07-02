
from django.contrib.contenttypes.fields import (
    GenericRelation, GenericForeignKey)
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import models
from treebeard.mp_tree import MP_Node

from fiesta.settings import api_settings
from fiesta.core.validators import re_validators, errors, clean_validators
from fiesta.core import constants
from fiesta.apps.common.models import managers 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH
TINY = api_settings.DEFAULT_TINY_STRING_LENGTH
LARGE = api_settings.DEFAULT_LARGE_STRING_LENGTH
REGULAR = api_settings.DEFAULT_STRING_LENGTH

class AnnotableArtefact(models.Model):
    annotation = GenericRelation('common.Annotation')

    class Meta:
        abstract = True

class IdentifiableArtefact(AnnotableArtefact):
    object_id = models.CharField('ID', max_length=SMALL,
                               validators=[re_validators['IDType']],
                               blank=True)

    class Meta:
        abstract = True
        ordering = ['object_id']
        indexes = [
            models.Index(fields=['object_id']),
        ]

    def __str__(self):
        return self.object_id 

class NameableArtefact(IdentifiableArtefact):
    name = GenericRelation('common.Text')
    description = GenericRelation('common.Text')

    class Meta(IdentifiableArtefact.Meta):
        abstract = True

class Item(NameableArtefact):
    wrapper = models.ForeignKey('MaintainableArtefact', on_delete=models.CASCADE)

    class Meta(NameableArtefact.Meta):
        abstract = True
        indexes = NameableArtefact.Meta.indexes[:] + [ 
            models.Index(fields=['wrapper']),
            models.Index(fields=['wrapper', 'object_id']),
        ]
        unique_together = ('wrapper', 'object_id')

class ItemWithParent(Item, MP_Node):

    objects = managers.ItemWithParentManager()

    class Meta(Item.Meta):
        abstract = True

    def clean(self):
        parent = self.get_parent()
        if parent:
            if self.wrapper != parent.wrapper:
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

class ManyToManyItemWithParent(NameableArtefact, MP_Node):

    objects = managers.ManyToManyItemWithParentManager()

    class Meta(NameableArtefact.Meta):
        abstract = True

    def clean(self):
        parent = self.get_parent()
        if parent:
            if not self.wrappers.intersection(parent.wrappers):
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

class VersionableArtefact(NameableArtefact):
    version = models.CharField(
        max_length=TINY, 
        validators=[re_validators['VersionType']], 
        default='1.0'
    )
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta(NameableArtefact.Meta):
        abstract = True
        indexes = IdentifiableArtefact.Meta.indexes[:] + [ 
            models.Index(fields=['object_id', 'version']),
        ]

class MaintainableArtefact(VersionableArtefact):
    object_id = models.CharField('ID', max_length=SMALL,
                               validators=[re_validators['IDType']])
    agency = models.ForeignKey('base.Organisation', on_delete=models.CASCADE) 
    is_final = models.BooleanField(default=False)
    submitted_structures = GenericRelation('registry.SubmittedStructure')
    latest = models.BooleanField(default=False)

    class Meta(VersionableArtefact.Meta):
        abstract = True
        unique_together = ('object_id', 'agency', 'version')
        indexes = [
            models.Index(fields=['object_id']),
            models.Index(fields=['agency']),
            models.Index(fields=['object_id', 'version']),
            models.Index(fields=['object_id','agency', 'version']),
        ]

    objects = managers.MaintainableManager() 

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.agency, self.version)

    def clean(self):
        # Block modification of final objects
        created = not bool(self.pk)
        if not created and self.is_final:
            raise clean_validators['MaintainableArtefact']['update']


class AbstractText(models.Model):
    objects = managers.TextManager()
    text = models.CharField(max_length=LARGE)
    text_type = models.CharField(max_length=SMALL,
                                 choices=constants.TEXT_TYPES, null=True,
                                 blank=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    nameable_object = GenericForeignKey()

    class Meta:
        abstract = True

class AbstractAnnotation(models.Model):
    object_id = models.CharField('ID', max_length=SMALL, blank=True)
    annotation_title = models.CharField('title', max_length=REGULAR,
                                        blank=True)
    annotation_type = models.CharField('type', max_length=SMALL, blank=True)
    annotation_url = models.URLField('URL', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    obj_id = models.PositiveIntegerField()
    annotable_object = GenericForeignKey('content_type', 'obj_id')
    annotation_text = GenericRelation('common.Text')

    class Meta:
        abstract = True

    objects = managers.AnnotationManager() 

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.annotation_title, self.annotation_type)

class AbstractFormat(models.Model):
    text_type = models.CharField(
        max_length=SMALL, 
        choices=constants.DATA_TYPES,
        null=True, blank=True
    )
    is_sequence = models.NullBooleanField(null=True, blank=True)
    interval = models.DecimalField(null=True, blank=True, max_digits=19,
                                   decimal_places=10)
    start_value = models.DecimalField(null=True, blank=True, max_digits=19,
                                      decimal_places=10)
    end_value = models.DecimalField(null=True, blank=True, max_digits=19,
                                    decimal_places=10)
    time_interval = models.DurationField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    min_value= models.DecimalField(null=True, blank=True, max_digits=19,
                                   decimal_places=10)
    max_value = models.DecimalField(null=True, blank=True, max_digits=19,
                                    decimal_places=10)
    decimals = models.PositiveIntegerField(null=True, blank=True)
    pattern = models.TextField(null=True, blank=True)
    is_multi_lingual = models.BooleanField(null=True, blank=True)

    class Meta:
        abstract = True

class AbstractRepresentation(models.Model):

    text_format = models.ForeignKey('Format', on_delete=models.CASCADE,
                                    null=True, blank=True,
                                    related_name='representation_text_formats')
    enumeration = models.ForeignKey('codelist.Codelist',
                                    on_delete=models.CASCADE, null=True,
                                    blank=True,
                                    related_name='enumerations')
    enumeration_format = models.ForeignKey(
        'Format', on_delete=models.CASCADE, null=True, blank=True,
        related_name='representation_enumeration_formats')

    class Meta:
        abstract = True
