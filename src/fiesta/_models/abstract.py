from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from treebeard.mp_tree import MP_Node

from ..settings import api_maxlen_settings as max_length 
from ..validators import re_validators, errors, clean_validators


class AnnotableArtefact(models.Model):
    annotation = GenericRelation('Annotation')

    class Meta:
        abstract = True

class IdentifiableArtefact(AnnotableArtefact):
    object_id = models.CharField('ID', max_length=max_length.OBJECT_ID,
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
    name = GenericRelation('Text')
    description = GenericRelation('Text')

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

# class RepresentedItem(Item, Representation):
#     class Meta(Item.Meta):
#         abstract = True

class ItemWithParent(Item, MP_Node):
    # parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

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


class VersionableArtefact(NameableArtefact):
    version = models.CharField(
        max_length=max_length.VERSION, 
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
    object_id = models.CharField('ID', max_length=max_length.OBJECT_ID,
                               validators=[re_validators['IDType']])
    agency = models.ForeignKey('Organisation', on_delete=models.CASCADE) 
    is_final = models.BooleanField(default=False)
    submitted_structures = GenericRelation('SubmittedStructure')

    class Meta(VersionableArtefact.Meta):
        abstract = True
        unique_together = ('object_id', 'agency', 'version')
        indexes = [
            models.Index(fields=['object_id']),
            models.Index(fields=['agency']),
            models.Index(fields=['object_id', 'version']),
            models.Index(fields=['object_id','agency', 'version']),
        ]

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.agency, self.version)

    def clean(self):
        # Make sure that final structures cannot be modified
        created = not bool(self.pk)
        if not created and self.is_final:
            raise clean_validators['MaintainableArtefact']['update']
