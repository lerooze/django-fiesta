# abstract_models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ...settings import api_settings
from ...core import constants
from ...core.validators import re_validators

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH
TINY = api_settings.DEFAULT_TINY_STRING_LENGTH
LARGE = api_settings.DEFAULT_LARGE_STRING_LENGTH
REGULAR = api_settings.DEFAULT_STRING_LENGTH

class AbstractBaseReference(models.Model):
    provisionagreement_set = models.ManyToManyField('registry.ProvisionAgreement')
    attachmentconstraint_set = models.ManyToManyField('registry.AttachmentConstraint')
    contentconstraint_set = models.ManyToManyField('registry.ContentConstraint')
    statusmessagetext_set = models.ManyToManyField('registry.StatusMessageText')

    class Meta:
        abstract = True

class Text(AbstractBaseReference, common.AbstractText):
    pass

class Annotation(AbstractBaseReference, common.AbstractAnnotation):
    pass

class Log(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name = _('User'))
    channel = models.CharField(
        _('Channel'),
        max_length=SMALL, 
        choices=constants.CHANNELS)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    progress = models.CharField(
        _('Progress'), 
        max_length=SMALL, 
        choices=constants.PROGRESS, 
        default='Processing', 
        editable=False)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    request_file = models.FileField(
        _('Request file'), 
        upload_to='requests/%Y/%m/%d/', 
        editable=False, 
        null=True)
    response_file = models.FileField(
        _('Response file'), 
        upload_to='responses/%Y/%m/%d/', 
        editable=False, 
        null=True)
    exceptions_file = models.FileField(
        _('exceptions_file'),
        upload_to='exceptions/%Y/%m/%d/', 
        editable=False, 
        null=True)

    class Meta:
        abstract = True
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')

    def update_progress(self, status):
        self.progress = status
        self.save()

class SubmitStructureRequest(models.Model):
    header = models.OneToOneField(
        'common.Header', 
        on_delete=models.PROTECT,
        verbose_name=_('Header')
    )
    action = models.CharField(
        _('Action'),
        max_length=SMALL, 
        choices=constants.ACTIONS, 
        default='A')
    structure_location = models.URLField(_('Structure location'), null=True)
    external_dependencies = models.BooleanField(
        _('External dependencies'),
        default=False)

    class Meta:
        abstract = True
        verbose_name = _('Submit structure request')
        verbose_name_plural = _('Submit structure requests')

class SubmittedStructure(models.Model):
    submit_structure_request = models.ForeignKey(
        'SubmitStructureRequest',
        on_delete=models.PROTECT,
        verbose_name=_('Submit structure request')
    )
    action = models.CharField(
        _('Action'),
        max_length=SMALL, 
        choices=constants.ACTIONS, 
        blank=True, 
        null=True)
    external_dependencies = models.BooleanField(
        _('External dependencies'),
        blank=True, 
        null=True)
    status_message = models.OneToOneField(
        'StatusMessage', 
        null=True, 
        on_delete=models.PROTECT,
        verbose_name=_('Status message')
    )

    class Meta:
        abstract = True
        verbose_name = _('Submitted structure')
        verbose_name_plural = _('Submitted structures')

class StatusMessage(models.Model):
    status = models.CharField(
        _('Status'), 
        max_length=SMALL, 
        choices=constants.STATUSES)
    message_text = models.ManyToManyField(
        'StatusMessageText',
        verbose_name=_('Message text')
    )

    class Meta:
        abstract = True
        verbose_name = _('Status message')
        verbose_name_plural = _('Status messages')

class StatusMessageText(models.Model):
    code = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['IDType']], 
        blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Status message text')
        verbose_name_plural = _('Status message texts')

class Header(models.Model):
    log = models.OneToOneField('registry.Log', on_delete=models.PROTECT)
    object_id = models.CharField(
        'ID', max_length=SMALL, validators=[re_validators['IDType']],
        editable=False)
    test = models.BooleanField(default=False)
    prepared = models.DateTimeField(null=True, blank=True, editable=False)
    sender = models.ForeignKey(
        'registry.Party', 
        on_delete=models.PROTECT, 
        editable=False, 
        related_name='+'
    )
    receiver = models.ForeignKey(
        'registry.Party', 
        on_delete=models.PROTECT, 
        editable=False, 
        related_name='+'
    )

    def __str__(self):
        kind = 'Test' if self.test else 'Actual'
        return f'{kind} submittion by {self.sender.object_id}'

    class Meta:
        abstract = True
        verbose_name = _('Header')
        verbose_name_plural = _('Headers')

class Party(common.AbstractItem):
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['IDType']],
        db_index=True
    )
    timezone = models.CharField(max_length=SMALL, blank=True)

    class Meta(common.AbstractItem.Meta):
        abstract = True
        verbose_name = _('Party')
        verbose_name_plural = _('Parties')

# class AbstractRegistration(models.Model):
#     submission = models.ForeignKey('Submission', on_delete=models.CASCADE)
#     action = models.CharField(
#         max_length=SMALL, choices=constants.ACTIONS, default='A')
#     provision_agreement = models.ForeignKey(
#         'ProvisionAgreement', on_delete=models.CASCADE)
#     data_source_file = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True)
#     data_source = models.ForeignKey(
#         'Datasource', on_delete=models.CASCADE)
#     id_code = models.CharField(
#         'ID', max_length=SMALL, validators=[re_validators['IDType']],
#         editable=True)
#     valid_from = models.DateTimeField(null=True, blank=True)
#     valid_to = models.DateTimeField(null=True, blank=True)
#     last_updated = models.DateTimeField(null=True, blank=True)
#     index_time_series = models.BooleanField(default=False)
#     index_data_set= models.BooleanField(default=False)
#     index_attributes = models.BooleanField(default=False)
#     index_reporting_period = models.BooleanField(default=False)
#     status_message = models.OneToOneField('StatusMessage', null=True)
#     status_message_file = models.FileField(
#         upload_to='uploads/%Y/%m/%d/', null=True, editable=False)
#
#     def __str__(self):
#         return '%s:%s:%s' % (self.submission.user, self.action, self.provision_agreement)
#
#     class Meta:
#         abstract = True
#     
# class AbstractDatasource(models.Model): 
#     simple_data_source = models.URLField(blank=True, null=True)
#     queryable_data_source = models.OneToOneField('QueryableDatasource',
#                                                   null=True)
#
#     class Meta:
#         abstract = True
#
# class AbstractQueryableDatasource(models.Model):
#     data_url = models.URLField()
#     wsdl_url = models.URLField(blank=True, null=True)
#     wadl_url = models.URLField(blank=True, null=True)
#     is_rest_data_source = models.BooleanField()
#     is_web_service_data_source = models.BooleanField()
#
#     class Meta:
#         abstract = True
#
# class AbstractRESTfulStructureQuery(models.Model):
#     log = models.OneToOneField('Log', on_delete=models.CASCADE)
#     resource = models.CharField(max_length=SMALL)
#     agency_id = models.CharField(max_length=SMALL)
#     resource_id = models.CharField(max_length=SMALL)
#     version = models.CharField(max_length=SMALL)
#     detail = models.CharField(max_length=SMALL)
#     references = models.CharField(max_length=SMALL)
#
#     class Meta:
#         abstract = True
#
# class AbstractRESTfulSchemaQuery(models.Model):
#     log = models.OneToOneField('Log', on_delete=models.CASCADE)
#     context = models.CharField(max_length=SMALL)
#     agency_id = models.CharField(max_length=SMALL)
#     resource_id = models.CharField(max_length=SMALL)
#     version = models.CharField(max_length=SMALL)
#     observation_dimension = models.CharField(max_length=SMALL)
#
#     class Meta:
#         abstract = True
#
# class AbstractProvisionAgreement(common.MaintainableArtefact):
#     content_constraint = models.ManyToManyField('registry.ContentConstraint')
#     dataflow = models.ForeignKey('datastructure.Dataflow', on_delete=models.PROTECT)
#     data_provider = models.ForeignKey('base.DataProvider', on_delete=models.PROTECT)
#
#     class Meta:
#         abstract = True
#
# class AbstractAttachmentConstraint(common.MaintainableArtefact):
#
#     class Meta:
#         abstract = True
#
# class AbstractContentConstraint(common.MaintainableArtefact):
#     release_calendar = models.ForeignField('ReleaseCalendar')
#     reference_period = models.ForeignField('common.ReferencePeriod')
#     tipe = models.models.CharField(_('type'), max_length=SMALL, choices=constants.CONTENT_CONSTRAINT_TYPE_CODE)
#
#     class Meta:
#         abstract = True
#
# class Region(models.Model):
#     attachment_constraint = models.ForeignKey('AttachmentConstraint', on_delete=models.CASCADE, null=True)
#     content_constraint = models.ForeignKey('ContentConstraint', on_delete=models.CASCADE, null=True)
#
#     class Meta:
#         abstract = True
#
# class AbstractKeySet(Region):
#     is_included = models.BooleanField()
#     
# class AbstactKey(models.Model):
#     key_set = models.ForeignKey('KeySet', on_delete=models.CASCADE)
#
# class AbstractSubKey(models.Model):
#     key = models.ForeignKey('Key', on_delete=models.CASCADE)
#     component_id = models.CharField(max_length=SMALL)
#     value = models.CharField(max_length=SMALL, blank=True)
#
# class AbstractCubeRegion(Region):
#     include = models.BooleanField()
#
# class AbstractCubeRegionKey(models.Model):
#     cube_region = models.ForeignKey('CubeRegion')
#     component_id = models.CharField(max_length=SMALL)
#
# class AbstractCubeRegionKeyValue(models.Model):
#     cube_region_key = models.ForeignKey('CubeRegionKey')
#     cascade_values = models.BooleanField(default=False)
#     value = models.CharField(max_length=SMALL, blank=True)
#
# class AbstractCubeRegionKeyTimeRange(models.Model):
#     cube_region_key = models.ForeignKey('CubeRegionKey')
#     before_period = models.ForeignKey('TimePeriod', null=True)
#     after_period = models.ForeignKey('TimePeriod', null=True)
#     start_period = models.ForeignKey('TimePeriod', null=True)
#     end_period = models.ForeignKey('TimePeriod', null=True)
#
# class TimePeriod(models.Model):
#     time_period = models.CharField(max_length=SMALL)
#     is_inclusive = models.BooleanField(default=True)
#
# class AbstractReleaseCalendar(models.Model):
#     periodicity = models.CharField(max_length=SMALL)
#     offset = models.CharField(max_length=SMALL)
#     tolerance = models.CharField(max_length=SMALL)
#
#     class Meta:
#         abstract = True

