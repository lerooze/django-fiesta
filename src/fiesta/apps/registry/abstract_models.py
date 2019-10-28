# abstract_models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common

VERY_SMALL = api_settings.DEFAULT_VERY_SMALL_STRING
SMALL = api_settings.DEFAULT_SMALL_STRING
MEDIUM = api_settings.DEFAULT_MEDIUM_STRING
TINY = api_settings.DEFAULT_TINY_STRING

ACTION_CHOICES = Choices(
    (0, 'APPEND', 'Append'),
    (1, 'REPLACE', 'Replace'),
    (2, 'DELETE', 'Delete'),
)

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
        (0, 'SUBMITTED', 'Submitted'),
        (1, 'NEGOTIATING', 'Negotiating'),
        (2, 'PARSING', 'Parsing'),
        (3, 'PROCESSING', 'Processing'),
        (4, 'COMPLETED', 'Completed'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name = _('User')
    )
    channel = models.IntegerField(
        _('Channel'),
        choices=CHANNEL_CHOICES,
        null=False,
        blank=False,
        editable=False
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
    ACTION_CHOICES = ACTION_CHOICES
    header = models.OneToOneField(
        'registry.Header', 
        on_delete=models.PROTECT,
        verbose_name=_('Header'),
    )
    structure_location = models.URLField(
        _('Structure location'), 
        null=True,
        blank=True
    )
    action = models.IntegerField(
        _('Action'),
        choices=ACTION_CHOICES, 
        default=0
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
    ACTION_CHOICES = ACTION_CHOICES
    submit_structure_request = models.ForeignKey(
        'registry.SubmitStructureRequest',
        on_delete=models.PROTECT,
        verbose_name=_('Submit structure request'),
    )
    action = models.IntegerField(
        _('Action'),
        choices=ACTION_CHOICES, 
        default=0
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

    class Meta:
        abstract = True
        verbose_name = _('Status message')
        verbose_name_plural = _('Status messages')

class ErrorCode(models.Model):
    # TODO complete ERROR_CODE_CHOICES
    ERROR_CODE_CHOICES = Choices(
        (1001, 'FIESTA_1001_HEADER_ORGANISATION_NOT_REGISTERED'),
        (1002, 'FIESTA_1002_HEADER_CONTACT_EMAIL_NOT_FOUND'),
    )
    class Code(models.IntegerChoices):
        FIESTA_1001_HEADER_ORGANISATION_NOT_REGISTERED = 1001, 

        
    status_message = models.ForeignKey(
        'registry.StatusMessage',
        on_delete=models.CASCADE,
        verbose_name=_('Status message')
    )
    code = models.IntegerField(
        _('Error code'), 
        choices=ERROR_CODE_CHOICES
    )

    class Meta:
        abstract = True
        verbose_name = _('Error code')
        verbose_name_plural = _('Error codes')

class Header(models.Model):
    ACTION_CHOICES = ACTION_CHOICES
    log = models.OneToOneField(
        'registry.Log', 
        on_delete=models.PROTECT,
        verbose_name=_('Log'),
        editable=False
    )
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['IDType']],
    )
    test = models.BooleanField(
        _('Test'),
        default=False,
    )
    prepared = models.DateTimeField(
        _('Prepared'),
        null=True, 
        blank=True, 
    )
    sender = models.OneToOneField(
        'registry.Party', 
        verbose_name=_('Sender'),
        on_delete=models.PROTECT, 
        related_name='+',
    )
    receiver = models.OneToOneField(
        'registry.Party', 
        verbose_name=_('Receiver'),
        on_delete=models.PROTECT, 
        related_name='+',
    )
    name = models.CharField(
        _('Transmission name'),
        max_length=MEDIUM,
        null=False,
    )
    structure = models.OneToOneField(
        'registry.PayloadStructure',
        on_delete=models.PROTECT,
        verbose_name=_('Structure'),
        null=True,
        blank=True
    )
    data_provider = models.ForeignKey(
        'base.DataProvider',
        verbose_name=_('Data provider'),
        on_delete=models.PROTECT,
        null=True,
    )
    data_set_action = models.IntegerField(
        _('Data set action'),
        choices=ACTION_CHOICES, 
        null=True,
        blank=True
    )
    data_set_id = models.CharField(
        _('Data set ID'),
        max_length=SMALL,
        blank=True
    )
    extracted = models.DateTimeField(
        _('Prepared'),
        null=True, 
        blank=True, 
    )
    extracted = models.DateTimeField(
        _('Extracted'), 
        auto_now=True,
    )
    reporting_begin = models.CharField(
        _('Reporting begin'),
        max_length=MEDIUM,
        blank=True
    )
    reporting_end = models.CharField(
        _('Reporting end'),
        max_length=MEDIUM,
        blank=True
    )
    embargo_date = models.DateTimeField(
        _('Embargo date'),
        null=True,
        blank=True
    )
    source = models.CharField(
        _('Source'),
        max_length=SMALL,
        blank=True
    )

    def __str__(self):
        kind = 'Test' if self.test else 'Actual'
        return f'{kind} submittion by {self.sender.object_id}'

    class Meta:
        abstract = True
        verbose_name = _('Header')
        verbose_name_plural = _('Headers')

class PayloadStructure(models.Model):
    provision_agreement = models.ForeignKey(
        'registry.ProvisionAgreementReference',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Provision agreement')
    )
    structure_usage = models.ForeignKey(
        'datastructure.DataflowReference',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Structure usage')
    )
    structure = models.ForeignKey(
        'datastructure.DataStructureReference',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Structure')
    )
    structure_id = models.CharField(
        _('Structure ID'),
        max_length=SMALL,
        null=False,
        blank=False
    )
    schema_url = models.URLField(
        _('Schema URL'),
        null=False,
        blank=True
    )
    namespace = models.CharField(
        _('Namespace'),
        max_length=MEDIUM,
        null=False,
        blank=True
    )
    dimension_at_observation = models.CharField(
        _('Observation dimension'),
        max_length=VERY_SMALL,
        null=False,
        blank=True
    )
    explicit_measures = models.BooleanField(
        _('Explicit measures'),
        null=True,
        blank=True
    )
    service_url = models.URLField(
        _('Service URL'),
        null=True,
        blank=True
    )
    structure_url = models.URLField(
        _('Structure URL'),
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Payload structure')
        verbose_name_plural = _('Payload structures')

class Party(common.AbstractNameable):
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['IDType']],
        db_index=True
    )
    timezone = models.CharField(max_length=SMALL, blank=True)

    class Meta(common.AbstractNameable.Meta):
        abstract = True
        verbose_name = _('Party')
        verbose_name_plural = _('Parties')

class Contact(common.AbstractContact):
    party = models.ForeignKey(
        'registry.Party',
        on_delete=models.CASCADE,
        verbose_name=_('Party'),
        related_name='contact_set',
        related_query_name='contact'
    )

    class Meta(common.AbstractContact.Meta):
        abstract = True

class Telephone(common.AbstractTelephone):
    contact = models.ForeignKey(
        'registry.Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='telephone_set',
        related_query_name='telephone',
    )

    class Meta(common.AbstractTelephone.Meta):
        abstract = True


class Fax(common.AbstractFax):
    contact = models.ForeignKey(
        'registry.Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='fax_set',
        related_query_name='fax',
    )

    class Meta(common.AbstractFax.Meta):
        abstract = True


class X400(common.AbstractX400):
    contact = models.ForeignKey(
        'registry.Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='x400_set',
        related_query_name='x400',
    )

    class Meta(common.AbstractX400.Meta):
        abstract = True


class Email(common.AbstractEmail):
    contact = models.ForeignKey(
        'registry.Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='email_set',
        related_query_name='email',
    )

    class Meta(common.AbstractEmail.Meta):
        abstract = True


class URI(common.AbstractURI):
    contact = models.ForeignKey(
        'registry.Contact',
        on_delete=models.CASCADE,
        verbose_name=_('Contact'),
        related_name='uri_set',
        related_query_name='uri',
    )

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

class Annotation(common.Annotation):
    provision_agreement = models.ForeignKey(
        'registry.ProvisionAgreement',
        on_delete=models.CASCADE,
        verbose_name=_('Provision agreement'),
        null=True,
        blank=True,
    )
    attachment_constraint = models.ForeignKey(
        'registry.AttachmentConstraint',
        on_delete=models.CASCADE,
        verbose_name=_('Attachment constraint'),
        null=True,
        blank=True,
    )
    content_constraint = models.ForeignKey(
        'registry.ContentConstraint',
        on_delete=models.CASCADE,
        verbose_name=_('Content constraint'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

class ProvisionAgreementReference(common.AbstractReference):
    class Meta(common.AbstractReference.Meta):
        abstract = True
        verbose_name = _('Provision agreement reference')
        verbose_name_plural = _('Provision agreement references')

class ProvisionAgreement(common.AbstractMaintainable):
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

class AttachmentConstraint(common.AbstractMaintainable):
    data_structures = models.ManyToManyField(
        'datastructure.DataStructureReference',
        verbose_name=_('Data structures')
    )

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Attachment constraint')
        verbose_name_plural = _('Attachment constraints')

class ContentConstraintReference(common.AbstractReference):
    class Meta(common.AbstractReference.Meta):
        abstract = True
        verbose_name = _('Content constraint reference')
        verbose_name_plural = _('Content constraint references')

class ContentConstraint(common.AbstractMaintainable):
    TYPE_CHOICES = Choices(
        (0, 'ACTUAL', 'Actual'),
        (1, 'ALLOWED', 'Allowed'),
    )
    data_provider = models.ForeignKey(
        'base.DataProviderReference',
        on_delete=models.PROTECT,
        verbose_name=_('Data provider'),
        null=True,
        blank=True
    )
    data_structures = models.ManyToManyField(
        'datastructure.DataStructureReference',
        verbose_name=_('Data structures')
    )
    dataflows = models.ManyToManyField(
        'datastructure.DataflowReference',
        verbose_name=_('Dataflows')
    )
    provision_agreements = models.ManyToManyField(
        'datastructure.ProvisionAgreement',
        verbose_name=_('Provision agreements')
    )
    release_calendar = models.ForeignKey(
        'registry.ReleaseCalendar',
        on_delete=models.CASCADE,
        verbose_name=_('Release calendar'),
        null=True,
        blank=True
    )
    reference_period = models.ForeignKey(
        'common.ReferencePeriod',
        on_delete=models.CASCADE,
        verbose_name=_('Reference period'),
        null=True,
        blank=True
    )
    tipe = models.IntegerField(
        _('type'), 
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES.ACTUAL
    )

    class Meta(common.AbstractMaintainable.Meta):
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
        'registry.ContentConstraint', 
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
    key_value = models.ForeignKey(
        'CubeRegion',
        on_delete=models.CASCADE,
        related_name='key_value_set',
        related_query_name='key_value', 
        verbose_name=_('Cube region')
    )
    attribute = models.ForeignKey(
        'CubeRegion',
        on_delete=models.CASCADE,
        related_name='attribute_set',
        related_query_name='attribute', 
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
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
    cube_region_key = models.OneToOneField(
        'CubeRegionKey',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Cube region key')
    )
    before_period = models.ForeignKey(
        'TimePeriod', 
        on_delete=models.CASCADE,
        verbose_name=_('Before period'),
        related_name='+',
        null=True
    )
    after_period = models.ForeignKey(
        'TimePeriod',
        on_delete=models.CASCADE,
        verbose_name=_('After period'),
        related_name='+',
        null=True
    )
    start_period = models.ForeignKey(
        'TimePeriod', 
        on_delete=models.CASCADE,
        verbose_name=_('Start period'),
        related_name='+',
        null=True,
    )
    end_period = models.ForeignKey(
        'TimePeriod', 
        on_delete=models.CASCADE,
        verbose_name=_('End period'),
        related_name='+',
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
