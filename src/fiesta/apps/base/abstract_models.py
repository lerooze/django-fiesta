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


class Annotation(common.Annotation):
    agency = models.ForeignKey(
        'base.Agency',
        on_delete=models.CASCADE,
        verbose_name=_('Agency'),
        null=True,
        blank=True,
    )
    data_provider_scheme = models.ForeignKey(
        'base.DataProviderScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Data provider scheme'),
        null=True,
        blank=True,
    )
    data_provider = models.ForeignKey(
        'base.DataProvider',
        on_delete=models.CASCADE,
        verbose_name=_('Data provider'),
        null=True,
        blank=True,
    )
    data_consumer_scheme = models.ForeignKey(
        'base.DataConsumerScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Data consumer scheme'),
        null=True,
        blank=True,
    )
    data_consumer = models.ForeignKey(
        'base.DataConsumer',
        on_delete=models.CASCADE,
        verbose_name=_('Data consumer'),
        null=True,
        blank=True,
    )
    organisation_unit_scheme = models.ForeignKey(
        'base.OrganisationUnitScheme',
        on_delete=models.CASCADE,
        verbose_name=_('Organisation unit scheme'),
        null=True,
        blank=True,
    )
    organistion_unit = models.ForeignKey(
        'base.OrganisationUnit',
        on_delete=models.CASCADE,
        verbose_name=_('Organisation unit'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


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
        related_name='contact_set',
        related_query_name='contact',
    )


class AgencyContactTelephone(common.AbstractTelephone):
    container = models.ForeignKey(
        'base.AgencyContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact person'),
        related_name='telephone_set',
        related_query_name='telephone',
    )

    class Meta(common.AbstractTelephone.Meta):
        abstract = True


class AgencyContactFax(common.AbstractFax):
    container = models.ForeignKey(
        'base.AgencyContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact person'),
        related_name='fax_set',
        related_query_name='fax',
    )

    class Meta(common.AbstractFax.Meta):
        abstract = True


class AgencyContactX400(common.AbstractX400):
    container = models.ForeignKey(
        'base.AgencyContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact person'),
        related_name='x400_set',
        related_query_name='x400',
    )

    class Meta(common.AbstractX400.Meta):
        abstract = True


class AgencyContactEmail(common.AbstractEmail):
    container = models.ForeignKey(
        'base.AgencyContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact person'),
        related_name='email_set',
        related_query_name='email',
    )

    class Meta(common.AbstractEmail.Meta):
        abstract = True


class AgencyContactURI(common.AbstractURI):
    container = models.ForeignKey(
        'base.AgencyContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact person'),
        related_name='uri_set',
        related_query_name='uri',
    )

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

    class Meta(common.AbstractItem.Meta):
        abstract = True
        verbose_name = _('Data provider')
        verbose_name_plural = _('Data providers')


class DataProviderContact(common.AbstractContact):
    container = models.ForeignKey(
        'base.DataProvider',
        on_delete=models.CASCADE,
        verbose_name=_('Data provider'),
        related_name='dataprovider_set',
        related_query_name='dataprovider',
    )


class DataProviderContactTelephone(common.AbstractTelephone):
    container = models.ForeignKey(
        'base.DataProviderContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='telephone_set',
        related_query_name='telephone'
    )

    class Meta(common.AbstractTelephone.Meta):
        abstract = True


class DataProviderContactFax(common.AbstractFax):
    container = models.ForeignKey(
        'base.DataProviderContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='fax_set',
        related_query_name='fax'
    )

    class Meta(common.AbstractFax.Meta):
        abstract = True


class DataProviderContactX400(common.AbstractX400):
    container = models.ForeignKey(
        'base.DataProviderContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='x400_set',
        related_query_name='x400'
    )

    class Meta(common.AbstractX400.Meta):
        abstract = True


class DataProviderContactEmail(common.AbstractEmail):
    container = models.ForeignKey(
        'base.DataProviderContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='email_set',
        related_query_name='email'
    )

    class Meta(common.AbstractEmail.Meta):
        abstract = True


class DataProviderContactURI(common.AbstractURI):
    container = models.ForeignKey(
        'base.DataProviderContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='uri_set',
        related_query_name='uri'
    )

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
        verbose_name=_('Data consumer'),
        related_name='contact_set',
        related_query_name='contact',
    )


class DataConsumerContactTelephone(common.AbstractTelephone):
    container = models.ForeignKey(
        'base.DataConsumerContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='telephone_set',
        related_query_name='telephone'
    )

    class Meta(common.AbstractTelephone.Meta):
        abstract = True


class DataConsumerContactFax(common.AbstractFax):
    container = models.ForeignKey(
        'base.DataConsumerContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='fax_set',
        related_query_name='fax'
    )

    class Meta(common.AbstractFax.Meta):
        abstract = True


class DataConsumerContactX400(common.AbstractX400):
    container = models.ForeignKey(
        'base.DataConsumerContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='x400_set',
        related_query_name='x400'
    )

    class Meta(common.AbstractX400.Meta):
        abstract = True


class DataConsumerContactEmail(common.AbstractEmail):
    container = models.ForeignKey(
        'base.DataConsumerContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='email_set',
        related_query_name='email'
    )

    class Meta(common.AbstractEmail.Meta):
        abstract = True


class DataConsumerContactURI(common.AbstractURI):
    container = models.ForeignKey(
        'base.DataConsumerContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='uri_set',
        related_query_name='uri'
    )

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
        verbose_name=_('Organisation unit'),
        related_name='contact_set',
        related_query_name='contact'
    )


class OrganisationUnitContactTelephone(common.AbstractTelephone):
    container = models.ForeignKey(
        'base.OrganisationUnitContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='telephone_set',
        related_query_name='telephone'
    )

    class Meta(common.AbstractTelephone.Meta):
        abstract = True


class OrganisationUnitContactFax(common.AbstractFax):
    container = models.ForeignKey(
        'base.OrganisationUnitContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='fax_set',
        related_query_name='fax'
    )

    class Meta(common.AbstractFax.Meta):
        abstract = True


class OrganisationUnitContactX400(common.AbstractX400):
    container = models.ForeignKey(
        'base.OrganisationUnitContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='x400_set',
        related_query_name='x400'
    )

    class Meta(common.AbstractX400.Meta):
        abstract = True


class OrganisationUnitContactEmail(common.AbstractEmail):
    container = models.ForeignKey(
        'base.OrganisationUnitContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='email_set',
        related_query_name='email'
    )

    class Meta(common.AbstractEmail.Meta):
        abstract = True


class OrganisationUnitContactURI(common.AbstractURI):
    container = models.ForeignKey(
        'base.OrganisationUnitContact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='uri_set',
        related_query_name='uri'
    )

    class Meta(common.AbstractURI.Meta):
        abstract = True
