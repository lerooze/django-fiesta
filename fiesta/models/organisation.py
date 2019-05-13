from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.conf import settings

from treebeard.mp_tree import MP_Node

from ..settings import api_maxlen_settings as max_length
from .abstract import MaintainableArtefact, NameableArtefact 

class OrganisationScheme(MaintainableArtefact):
    pass

class Organisation(NameableArtefact, MP_Node):
    schemes = models.ManyToManyField(OrganisationScheme, blank=True,
                                     related_name='organisations')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    class Meta(NameableArtefact.Meta):
        unique_together = ('object_id',)

    def __str__(self):
        return self.object_id 

    def save(self, **kwargs):
        if not self.depth:
            if self.parent_id:
                self.depth = self.parent.depth + 1
                self.parent.add_child(instance=self)
            else:
                self.add_root(instance=self)

            return  #add_root and add_child save as well
        super().save(**kwargs)

class Contact(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                     related_name='organisation_contacts')
    names = GenericRelation('Text')
    roles = GenericRelation('Text')
    departments = GenericRelation('Text')

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['organisation']),
            models.Index(fields=['user', 'organisation']),
        ]
        unique_together = ('user', 'organisation')

    def __str__(self):
        return '%s: %s' % (self.user, self.organisation)

class Telephone(models.Model):
    value = models.CharField('phone', max_length=max_length.TELEPHONE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,
                                related_name='telephones')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class Fax(models.Model):
    value = models.CharField('FAX', max_length=max_length.TELEPHONE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,
                                related_name='faxes')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class X400(models.Model):
    value = models.CharField('X400', max_length=max_length.X400)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,
                                related_name='x400s')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class URI(models.Model):
    value = models.URLField('URI')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,
                                related_name='uris')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class Email(models.Model):
    value = models.EmailField('email address')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,
                                related_name='emails')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']
