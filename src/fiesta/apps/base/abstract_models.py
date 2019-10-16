# abstract_models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING

class User(AbstractUser):
    agency = models.ForeignKey(
        'agency', 
        null=True, 
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('Agency'))
    data_provider = models.ForeignKey(
        'base.DataProvider', 
        null=True, 
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('Data provider'))
    data_consumer = models.ForeignKey(
        'base.DataConsumer', 
        null=True, 
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('Data consumer'))

    class Meta(AbstractUser.Meta):
        abstract = True
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class Agency(common.AbstractNestedNCNameNameable):

    class Meta:
        abstract = True
        verbose_name = _('Agency')
        verbose_name_plural = _('Agencies')

    def clean(self):
        pass

class AgencyContact(common.AbstractContact):
    container = models.ForeignKey(
        'base.Agency',
        on_delete=models.CASCADE,
        verbose_name=_('Agency'),
    )

class AbstractAgencyContactInfo(models.Model):
    container = models.ForeignKey(
        'base.AgencyContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact person'),
    )

    class Meta:
        abstract = True

class AgencyContactTelephone(AbstractAgencyContactInfo, common.AbstractTelephone):

    class Meta(common.AbstractTelephone.Meta):
        abstract = True

class AgencyContactFax(AbstractAgencyContactInfo, common.AbstractFax):

    class Meta(common.AbstractFax.Meta):
        abstract = True

class AgencyContactX400(AbstractAgencyContactInfo, common.AbstractX400):

    class Meta(common.AbstractX400.Meta):
        abstract = True

class AgencyContactEmail(AbstractAgencyContactInfo, common.AbstractEmail):

    class Meta(common.AbstractEmail.Meta):
        abstract = True

class AgencyContactURI(AbstractAgencyContactInfo, common.AbstractURI):

    class Meta(common.AbstractURI.Meta):
        abstract = True

class DataProviderScheme(common.AbstractMaintainable):

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Data provider scheme')
        verbose_name_plural = _('Data provider schemes')

class DataProviderReference(common.AbstractItemReference):

    class Meta(common.AbstractItemReference.Meta):
        abstract = True

class DataProvider(common.AbstractItem):
    container = models.ForeignKey(
        'base.DataProviderScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Data provider scheme')
    )
    content_constraint = models.ForeignKey(
        'registry.ContentConstraintReference',
        on_delete=models.SET_NULL,
        verbose_name=_('Content constraint'),
        null=True
    )

    class Meta(common.AbstractItem.Meta):
        abstract = True
        verbose_name = _('Data provider')
        verbose_name_plural = _('Data providers')

class DataProviderContact(common.AbstractContact):
    container = models.ForeignKey(
        'base.DataProvider',
        on_delete=models.CASCADE,
        verbose_name=_('Data provider')
    )

class AbstractDataProviderContactInfo(models.Model):
    container = models.ForeignKey(
        'base.DataProviderContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True

class DataProviderContactTelephone(AbstractDataProviderContactInfo, common.AbstractTelephone):

    class Meta(common.AbstractTelephone.Meta):
        abstract = True

class DataProviderContactFax(AbstractDataProviderContactInfo, common.AbstractFax):

    class Meta(common.AbstractFax.Meta):
        abstract = True

class DataProviderContactX400(AbstractDataProviderContactInfo, common.AbstractX400):

    class Meta(common.AbstractX400.Meta):
        abstract = True

class DataProviderContactEmail(AbstractDataProviderContactInfo, common.AbstractEmail):

    class Meta(common.AbstractEmail.Meta):
        abstract = True

class DataProviderContactURI(AbstractDataProviderContactInfo, common.AbstractURI):

    class Meta(common.AbstractURI.Meta):
        abstract = True

class DataConsumerScheme(common.AbstractMaintainable):

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Data consumer scheme')
        verbose_name_plural = _('Data consumer schemes')

class DataConsumer(common.AbstractItem):
    container = models.ForeignKey(
        'base.DataConsumerScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Data consumer scheme')
    )

    class Meta(common.AbstractItem.Meta):
        abstract = True
        verbose_name = _('Data consumer')
        verbose_name_plural = _('Data consumers')

class DataConsumerContact(common.AbstractContact):
    container = models.ForeignKey(
        'base.DataConsumer',
        on_delete=models.CASCADE,
        verbose_name=_('Data consumer')
    )

class AbstractDataConsumerContactInfo(models.Model):
    container = models.ForeignKey(
        'base.DataConsumerContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True

class DataConsumerContactTelephone(AbstractDataConsumerContactInfo, common.AbstractTelephone):

    class Meta(common.AbstractTelephone.Meta):
        abstract = True

class DataConsumerContactFax(AbstractDataConsumerContactInfo, common.AbstractFax):

    class Meta(common.AbstractFax.Meta):
        abstract = True

class DataConsumerContactX400(AbstractDataConsumerContactInfo, common.AbstractX400):

    class Meta(common.AbstractX400.Meta):
        abstract = True

class DataConsumerContactEmail(AbstractDataConsumerContactInfo, common.AbstractEmail):

    class Meta(common.AbstractEmail.Meta):
        abstract = True

class DataConsumerContactURI(AbstractDataConsumerContactInfo, common.AbstractURI):

    class Meta(common.AbstractURI.Meta):
        abstract = True

class OrganisationUnitScheme(common.AbstractMaintainable):

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Organisation unit scheme')
        verbose_name_plural = _('Organisation unit schemes')

class OrganisationUnit(common.AbstractItemWithParent):
    container = models.ForeignKey(
        'base.OrganisationUnitScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Organisation unit scheme')
    )

    class Meta(common.AbstractItemWithParent.Meta):
        abstract = True
        verbose_name = _('Organisation unit')
        verbose_name_plural = _('Organisation units')

class OrganisationUnitContact(common.AbstractContact):
    container = models.ForeignKey(
        'base.OrganisationUnit',
        on_delete=models.CASCADE,
        verbose_name=_('Organisation unit')
    )

class AbstractOrganisationUnitContactInfo(models.Model):
    container = models.ForeignKey(
        'base.OrganisationUnitContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True

class OrganisationUnitContactTelephone(AbstractOrganisationUnitContactInfo, common.AbstractTelephone):

    class Meta(common.AbstractTelephone.Meta):
        abstract = True

class OrganisationUnitContactFax(AbstractOrganisationUnitContactInfo, common.AbstractFax):

    class Meta(common.AbstractFax.Meta):
        abstract = True

class OrganisationUnitContactX400(AbstractOrganisationUnitContactInfo, common.AbstractX400):

    class Meta(common.AbstractX400.Meta):
        abstract = True

class OrganisationUnitContactEmail(AbstractOrganisationUnitContactInfo, common.AbstractEmail):

    class Meta(common.AbstractEmail.Meta):
        abstract = True

class OrganisationUnitContactURI(AbstractOrganisationUnitContactInfo, common.AbstractURI):

    class Meta(common.AbstractURI.Meta):
        abstract = True
