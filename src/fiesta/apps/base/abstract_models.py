# abstract_models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...core.validators import re_validators
from ...settings import api_settings

from ..common import abstract_models as common

from . import managers

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class User(AbstractUser):
    agency = models.ForeignKey(
        'agency', 
        null=True, 
        blank=True,
        verbose_name=_('Agency'))
    data_provider = models.ForeignKey(
        'data_provider', 
        null=True, 
        blank=True,
        verbose_name=_('Data provider'))
    data_consumer = models.ForeignKey(
        'data_consumer', 
        null=True, 
        blank=True,
        verbose_name=_('Data consumer'))

    class Meta(AbstractUser.Meta):
        abstract = True
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class Versionable(common.AbstractVersionable):
    organisationunitscheme = models.ForeignKey(
        'base.OrganisationUnitScheme',
        verbose_name=_('Organisation unit scheme')
    )

    class Meta(common.AbstractVersionable.Meta):
        abstract = True

class AbstractBase(models.Model):
    name = models.ForeignKey(
        'common.MediumString', 
        verbose_name=_('Name'), 
        related_name='+',
        null=True)
    description = models.ForeignKey(
        'common.LargeString', 
        verbose_name=_('Description'), 
        related_name='+',
        null=True)
    annotations = models.ManyToManyField(
        'common.Annotation',
        verbose_name=_('Annotations'),
        related_name='+'
    )

    class Meta:
        abstract = True

class Agency(AbstractBase, common.AbstractNestedNCNameIDItemWithParent):
    contacts = models.ManyToManyField(
        'base.Contact',
        verbose_name=_('Contacts'),
    )

    objects = managers.AgencyManager()

    class Meta(common.AbstractItemWithParent.Meta):
        abstract = True
        verbose_name = _('Agency')
        verbose_name_plural = _('Agencies')

    def clean(self):
        pass

class DataProviderScheme(AbstractBase, common.AbstractIDMaintainable):
    items = models.ManyToManyField(
        'base.DataProvider',
        verbose_name=_('Data providers'))

    class Meta(common.AbstractIDMaintainable.Meta):
        abstract = True
        verbose_name = _('Data provider scheme')
        verbose_name_plural = _('Data provider schemes')

class DataProvider(AbstractBase, common.AbstractIDItem):
    # contentconstraints = models.ManyToManyField(
    #     'registry.ContentConstraint',
    #     verbose_name=_('Content constraints'),
    #     through='base.ContentConstraintThrough'
    # )
    contacts = models.ManyToManyField(
        'base.Contact',
        verbose_name=_('Contacts'),
    )

    class Meta(common.AbstractIDItem.Meta):
        abstract = True
        verbose_name = _('Data provider')
        verbose_name_plural = _('Data providers')

class DataConsumerScheme(common.AbstractIDMaintainable):
    items = models.ManyToManyField(
        'base.DataConsumer',
        verbose_name=_('Data consumers'))

    class Meta(common.AbstractIDMaintainable.Meta):
        abstract = True
        verbose_name = _('Data consumer scheme')
        verbose_name_plural = _('Data consumer schemes')

class DataConsumer(common.AbstractIDItem):
    contacts = models.ManyToManyField(
        'base.Contact',
        verbose_name=_('Contacts'),
    )

    class Meta(common.AbstractIDItem.Meta):
        abstract = True
        verbose_name = _('Data consumer')
        verbose_name_plural = _('Data consumers')

class OrganisationUnitScheme(common.AbstractIDMaintainable):

    class Meta(common.AbstractIDMaintainable.Meta):
        abstract = True
        verbose_name = _('Organisation unit scheme')
        verbose_name_plural = _('Organisation unit schemes')

class VersionableOrganisationUnitScheme(common.Versionable):
    organisationunitscheme = models.ForeignKey(
        'base.OrganisationUnitScheme',
        verbose_name=_('Organisation unit scheme')
    )
    items = models.ManyToManyField(
        'base.OrganisationUnit',
        verbose_name=_('Organisation units')
    )

class AbstractItemBase(models.Model):
    name = models.ManyToManyField(
        'common.MediumString', 
        verbose_name=_('Name'), 
        through='ItemBaseDetail',
        null=True)
    description = models.ManyToManyField(
        'common.Description', 
        verbose_name=_('Description'), 
        through='ItemBaseDetail',
        null=True)
    annotations = models.ManyToManyField(
        'common.Annotation',
        verbose_name=_('Annotations'),
        through='ItemBaseDetail',
        related_name='+'
    )
    class Meta:
        abstract = True

class Through(common.AbstractThrough):
    organisationunit = models.ForeignKey(
        'base.OrganisationUnit',
        null=True,
        on_delete=models.CASCADE
    )
    organisationunitscheme = models.ForeignKey(
        'base.VersionableOrganisationUnitScheme',
        null=True,
        on_delete=models.CASCADE
    )

class OrganisationUnit(common.AbstractIDItemWithParent, base.AbstractItemBase):
    contacts = models.ManyToManyField(
        'Contact',
        
    )

    class Meta(common.AbstractItemWithParent.Meta):
        abstract = True
        verbose_name = _('Organisation unit')
        verbose_name_plural = _('Organisation units')

class AbstractContactReference(models.Model):
    agency_set = models.ManyToManyField('base.Agency')
    dataprovider_set = models.ManyToManyField('base.DataProvider')
    dataconsumer_set = models.ManyToManyField('base.DataConsumer')
    versionable_set = models.ManyToManyField('base.Versionable')
    party_set = models.ManyToManyField('registry.Party')

    class Meta:
        abstract = True

class Contact(AbstractContactReference):
    name = models.CharField(
        max_length=SMALL,
        verbose_name=_('Name'))
    derartment = models.CharField(
        max_length=SMALL,
        verbose_name=_('Department'))
    role = models.CharField(
        max_length=SMALL,
        verbose_name=_('Role'))

    class Meta:
        abstract = True
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

class Telephone(models.Model):
    value = models.CharField(_('phone'), max_length=SMALL)
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True
        verbose_name = _('Telephone')
        verbose_name_plural = _('Telephones')

class Fax(models.Model):
    value = models.CharField(_('FAX'), max_length=SMALL)
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True
        verbose_name = _('Fax')
        verbose_name_plural = _('Faxes')

class X400(models.Model):
    value = models.CharField(_('X400'), max_length=SMALL)
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True
        verbose_name = _('X400')
        verbose_name_plural = _('X400s')

class AbstractURI(models.Model):
    value = models.URLField(_('URI'))
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True
        verbose_name = _('URI')
        verbose_name_plural = _('URIs')

class AbstractEmail(models.Model):
    value = models.EmailField(_('Email'))
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')
