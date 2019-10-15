# abstract_models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH
TINY = api_settings.DEFAULT_TINY_STRING_LENGTH
LARGE = api_settings.DEFAULT_LARGE_STRING_LENGTH
REGULAR = api_settings.DEFAULT_STRING_LENGTH

class Log(models.Model):
    CHANNEL_CHOICES = Choices(
        (0, 'UPLOADSTRUCTUREGUI', 'UploadStructureGUI'),
        (1, 'UPLOADSTRUCTUREREST', 'UploadStructureREST'),
        (2, 'UPLOADDATAGUI', 'UploadDataGUI'),
        (3, 'UPLOADDATAREST', 'UploadDataREST'),
        (4, 'REQUESTSTRUCTUREGUI', 'RequestStructureGUI'),
        (5, 'REQUESTSTRUCTUREREST', 'RequestStructureREST'),
        (6, 'REQUESTDATAGUI', 'RequestDataGUI'),
        (7, 'REQUESTDATAREST', 'RequestDataREST'),
    )
    PROGRESS_CHOICES = Choices(
        (0, 'PROCESSING', 'Processing'),
        (1, 'FINISHED', 'Finished'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name = _('User')
    )
    channel = models.CharField(
        _('Channel'),
        max_length=SMALL, 
        choices=CHANNEL_CHOICES,
    )
    created = models.DateTimeField(
        _('Created'), 
        auto_now_add=True
    )
    progress = models.CharField(
        _('Progress'), 
        max_length=SMALL, 
        choices=PROGRESS_CHOICES, 
        default=PROGRESS_CHOICES.PROCESSING, 
        editable=False
    )
    updated = models.DateTimeField(
        _('Updated'), auto_now=True
    )
    request_file = models.FileField(
        _('Request file'), 
        upload_to='requests/%Y/%m/%d/', 
        editable=False, 
        null=True
    )
    response_file = models.FileField(
        _('Response file'), 
        upload_to='responses/%Y/%m/%d/', 
        editable=False, 
        null=True
    )
    exceptions_file = models.FileField(
        _('exceptions_file'),
        upload_to='exceptions/%Y/%m/%d/', 
        editable=False, 
        null=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')

    def update_progress(self, status):
        self.progress = status
        self.save()

class SubmitStructureRequest(models.Model):
    ACTION_CHOICES = Choices(
        (0, 'APPEND', 'Append'),
        (1, 'REPLACE', 'Replace'),
        (2, 'DELETE', 'Delete'),
    )
    header = models.OneToOneField(
        'common.Header', 
        on_delete=models.PROTECT,
        verbose_name=_('Header')
    )
    action = models.IntegerField(
        _('Action'),
        choices=ACTION_CHOICES, 
        default=ACTION_CHOICES.APPEND
    )
    structure_location = models.URLField(
        _('Structure location'), 
        null=True,
        blank=True
    )
    external_dependencies = models.BooleanField(
        _('External dependencies'),
        default=False
    )

    class Meta:
        abstract = True
        permissions = [
            ('maintainable', 'Can perform CRUD operations on maintainable artefacts')
        ]
        verbose_name = _('Submit structure request')
        verbose_name_plural = _('Submit structure requests')

class SubmittedStructure(models.Model):
    ACTION_CHOICES = Choices(
        (0, 'APPEND', 'Append'),
        (1, 'REPLACE', 'Replace'),
        (2, 'DELETE', 'Delete'),
    )
    submit_structure_request = models.ForeignKey(
        'SubmitStructureRequest',
        on_delete=models.PROTECT,
        verbose_name=_('Submit structure request')
    )
    action = models.IntegerField(
        _('Action'),
        choices=ACTION_CHOICES, 
        default=ACTION_CHOICES.APPEND
    )
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
    STATUS_CHOICES = Choices(
        (0, 'SUCCESS', 'Success'),
        (1, 'WARNING', 'Warning'),
        (2, 'FAILURE', 'Failure')
    )
    status = models.IntegerField(
        _('Status'), 
        choices=STATUS_CHOICES
    )
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
    sender = models.OneToOneField(
        'registry.Party', 
        on_delete=models.PROTECT, 
        editable=False, 
    )
    receiver = models.OneToOneField(
        'registry.Party', 
        on_delete=models.PROTECT, 
        editable=False, 
    )

    def __str__(self):
        kind = 'Test' if self.test else 'Actual'
        return f'{kind} submittion by {self.sender.object_id}'

    class Meta:
        abstract = True
        verbose_name = _('Header')
        verbose_name_plural = _('Headers')

class Party(common.AbstractNameable, common.AbstractContactMixin):
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

class Contact(common.AbstractContact):
    party = models.ForeignKey(
        'registry.Party',
        on_delete=models.CASCADE,
        verobse_name=_('Party')
    )

class AbstractContactInfo(models.Model):
    contact = models.ForeignKey(
        'registry.Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact')
    )

    class Meta:
        abstract = True

class Telephone(AbstractContactInfo, common.AbstractTelephone):

    class Meta(common.AbstractTelephone.Meta):
        abstract = True

class Fax(AbstractContactInfo, common.AbstractFax):

    class Meta(common.AbstractFax.Meta):
        abstract = True

class X400(AbstractContactInfo, common.AbstractX400):

    class Meta(common.AbstractX400.Meta):
        abstract = True

class Email(AbstractContactInfo, common.AbstractEmail):

    class Meta(common.AbstractEmail.Meta):
        abstract = True

class URI(AbstractContactInfo, common.AbstractURI):

    class Meta(common.AbstractURI.Meta):
        abstract = True

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

class ProvisionAgreementReference(common.AbstractReference):
    class Meta(common.AbstractReference.Meta):
        abstract = True
        verbose_name = _('Provision agreement reference')
        verbose_name_plural = _('Provision agreement references')

class ProvisionAgreement(common.AbstractMaintainable):
    content_constraint = models.ForeignKey(
        'registry.ContentConstraintReference',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Content constraint reference')
    )
    dataflow = models.ForeignKey(
        'registry.ProvisionAgreementReference', 
        on_delete=models.PROTECT,
        verbose_name=_('Provision agreement reference')
    )
    dataprovider = models.ForeignKey(
        'base.DataProviderReference', 
        on_delete=models.PROTECT,
        verbose_name=_('Data provider reference')
    )

    class Meta:
        abstract = True
        verbose_name = _('Provision agreement')
        verbose_name_plural = _('Provision agreements')

class AttachmentConstraintReference(common.AbstractReference):
    class Meta(common.AbstractReference.Meta):
        abstract = True
        verbose_name = _('Attachment constraint reference')
        verbose_name_plural = _('Attachment constraint references')

class AttachmentConstraint(common.Maintainable):

    class Meta(common.Maintainable.Meta):
        abstract = True
        verbose_name = _('Attachment constraint')
        verbose_name_plural = _('Attachment constraints')

class ContentConstraintReference(common.AbstractReference):
    class Meta(common.AbstractReference.Meta):
        abstract = True
        verbose_name = _('Content constraint reference')
        verbose_name_plural = _('Content constraint references')

class ContentConstraint(common.Maintainable):
    TYPE_CHOICES = (
        (0, 'ACTUAL', 'Actual'),
        (1, 'ALLOWED', 'Allowed'),
    )
    release_calendar = models.ForeignField(
        'registry.ReleaseCalendar',
        on_delete=models.CASCADE,
        verbose_name=_('Release calendar'),
        null=True
    )
    reference_period = models.ForeignField(
        'common.ReferencePeriod',
        on_delete=models.CASCADE,
        verbose_name=_('Reference period'),
        null=True
    )
    tipe = models.models.IntegerField(
        _('type'), 
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES.ACTUAL
    )

    class Meta(common.Maintainable.Meta):
        abstract = True
        verbose_name = _('Content constraint')
        verbose_name_plural = _('Content constraints')

class AbstractRegion(models.Model):
    attachment_constraint = models.ForeignKey(
        'registry.AttachmentConstraint', 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name=_('Attachment constraint')
    )
    content_constraint = models.ForeignKey(
        'registy.ContentConstraint', 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name=_('Content constraint')
    )

    class Meta:
        abstract = True

class KeySet(AbstractRegion):
    is_included = models.BooleanField(_('Is included'))

    class Meta:
        abstract = True
        verbose_name = _('Key set')
        verbose_name_plural = _('Key sets')

class Key(models.Model):
    key_set = models.ForeignKey(
        'registry.KeySet', 
        on_delete=models.CASCADE,
        verbose_name=_('Key set')
    )

    class Meta:
        abstract = True
        verbose_name = _('Key')
        verbose_name_plural = _('Keys')

class SubKey(models.Model):
    key = models.ForeignKey(
        'registry.Key', 
        on_delete=models.CASCADE,
        verbose_name=_('Key')
    )
    component_id = models.CharField(
        _('Component ID'),
        max_length=SMALL
    )
    value = models.CharField(
        _('Value'),
        max_length=SMALL,
        blank=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Sub key')
        verbose_name_plural = _('Sub keys')

class CubeRegion(AbstractRegion):
    include = models.BooleanField(_('include'))

    class Meta:
        abstract = True
        verbose_name = _('Cube region')
        verbose_name_plural = _('Cube regions')

class CubeRegionKey(models.Model):
    cube_region = models.ForeignKey(
        'CubeRegion',
        verbose_name=_('Cube region')
    )
    component_id = models.CharField(
        _('Component ID'),
        max_length=SMALL
    )

    class Meta:
        abstract = True
        verbose_name = _('Cube region key')
        verbose_name_plural = _('Cube region keys')

class CubeRegionKeyValue(models.Model):
    cube_region_key = models.ForeignKey(
        'CubeRegionKey',
        verbose_name=_('Cube region key')
    )
    cascade_values = models.BooleanField(
        _('Cascade values'),
        default=False
    )
    value = models.CharField(
        _('Value'),
        max_length=SMALL, 
        blank=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Cube region key value')
        verbose_name_plural = _('Cube region key values')

class CubeRegionKeyTimeRange(models.Model):
    cube_region_key = models.ForeignKey(
        'CubeRegionKey',
        verbose_name=_('Cube region key')
    )
    before_period = models.ForeignKey(
        'TimePeriod', 
        verbose_name=_('Before period'),
        null=True
    )
    after_period = models.ForeignKey(
        'TimePeriod',
        verbose_name=_('After period'),
        null=True
    )
    start_period = models.ForeignKey(
        'TimePeriod', 
        verbose_name=_('Start period'),
        null=True,
    )
    end_period = models.ForeignKey(
        'TimePeriod', 
        verbose_name=_('End period'),
        null=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Cube region key time range')
        verbose_name_plural = _('Cube region key time ranges')

class TimePeriod(models.Model):
    time_period = models.CharField(
        _('Time period'),
        max_length=SMALL
    )
    is_inclusive = models.BooleanField(
        _('Is inclusive'),
        default=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Time period')
        verbose_name_plural = _('Time periods')

class ReleaseCalendar(models.Model):
    periodicity = models.CharField(
        _('Periodicity'),
        max_length=TINY
    )
    offset = models.CharField(
        _('Offset'),
        max_length=SMALL
    )
    tolerance = models.CharField(
        _('Tolerance'),
        max_length=SMALL
    )

    class Meta:
        abstract = True
        verbose_name = _('Release calendar')
        verbose_name_plural = _('Release calendars')
