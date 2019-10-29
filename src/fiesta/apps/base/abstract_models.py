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


class Annotation(common.AbstractAnnotation):
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


class DataProviderScheme(common.AbstractMaintainable):

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Data provider scheme')
        verbose_name_plural = _('Data provider schemes')


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
