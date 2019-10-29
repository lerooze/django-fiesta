# abstract_models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from versionfield import VersionField

from ...settings import api_settings
from ...core.validators import re_validators

from ..common import abstract_models as common

VERY_SMALL = api_settings.DEFAULT_VERY_SMALL_STRING
SMALL = api_settings.DEFAULT_SMALL_STRING
MEDIUM = api_settings.DEFAULT_MEDIUM_STRING
TINY = api_settings.DEFAULT_TINY_STRING

class Action(models.IntegerChoices):
    APPEND = 0, _('Append')
    REPLACE = 1, _('Replace')
    DELETE = 2, _('Delete')
    INFORMATION = 3, _('Information')

class Log(models.Model):


    class Channel(models.IntegerChoices):
        UPLOADSTRUCTUREGUI = 0, _('UploadStructureGUI')
        UPLOADSTRUCTUREREST = 1, _('UploadStructureREST')
        UPLOADDATAGUI = 2, _('UploadDataGUI')
        UPLOADDATAREST = 3, _('UploadDataREST')
        REQUESTSTRUCTUREGUI = 4, _('RequestStructureGUI')
        REQUESTSTRUCTUREREST = 5, _('RequestStructureREST')
        REQUESTDATAGUI = 6, _('RequestDataGUI')
        REQUESTDATAREST = 7, _('RequestDataREST')


    class Progress(models.IntegerChoices):
        SUBMITTED = 0, _('Submitted')
        NEGOTIATING = 1, _('Negotiating')
        PARSING = 2, _('Parsing')
        PROCESSING = 3, _('Processing')
        COMPLETED = 4, _('Completed')


    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name = _('User')
    )
    channel = models.IntegerField(
        _('Channel'),
        choices=Channel.choices,
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
        choices=Progress.choices, 
        default=Progress.PROCESSING, 
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
        choices=Action.choices, 
        default=Action.APPEND
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
    submit_structure_request = models.ForeignKey(
        'registry.SubmitStructureRequest',
        on_delete=models.PROTECT,
        verbose_name=_('Submit structure request'),
    )
    action = models.IntegerField(
        _('Action'),
        choices=Action.choices, 
        default=Action.APPEND
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


    class Status(models.IntegerChoices):
        SUCCESS = 0, _('Success')
        WARNING = 1, _('Warning')
        FAILURE = 2, _('Failure')

    status = models.IntegerField(
        _('Status'), 
        choices=Status.choices
    )

    class Meta:
        abstract = True
        verbose_name = _('Status message')
        verbose_name_plural = _('Status messages')


class ErrorCode(models.Model):
    # TODO complete Error


    class Error(models.IntegerChoices):
        pass


    status_message = models.ForeignKey(
        'registry.StatusMessage',
        on_delete=models.CASCADE,
        verbose_name=_('Status message')
    )
    code = models.IntegerField(
        _('Error code'),
        choices=Error.choices
    )

    class Meta:
        abstract = True
        verbose_name = _('Error code')
        verbose_name_plural = _('Error codes')


class Header(models.Model):
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
        choices=Action.choices, 
        null=True,
        blank=True
    )
    data_set_id = models.CharField(
        _('Data set ID'),
        max_length=SMALL,
        blank=True
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
        'registry.ProvisionAgreement',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Provision agreement')
    )
    structure_usage = models.ForeignKey(
        'datastructure.Dataflow',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Structure usage')
    )
    structure = models.ForeignKey(
        'datastructure.DataStructure',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Structure')
    )
    structure_code = models.CharField(
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


class Party(models.Model):
    object_id = models.CharField(
        _('ID'), 
        max_length=SMALL, 
        validators=[re_validators['IDType']],
        db_index=True
    )
    name = models.CharField(
        _('Name'),
        max_length=MEDIUM,
        blank=True
    )
    timezone = models.CharField(max_length=SMALL, blank=True)

    class Meta:
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

class Annotation(common.AbstractAnnotation):
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


class ProvisionAgreement(common.AbstractMaintainable):
    dataflow = models.ForeignKey(
        'registry.ProvisionAgreement', 
        on_delete=models.PROTECT,
        verbose_name=_('Provision agreement')
    )
    dataflow_version = VersionField(
        _('Dataflow version'),
    )
    dataprovider = models.ForeignKey(
        'base.DataProvider', 
        on_delete=models.PROTECT,
        verbose_name=_('Data provider')
    )
    dataprovider_version = VersionField(
        _('Data provider version'),
    )

    class Meta:
        abstract = True
        verbose_name = _('Provision agreement')
        verbose_name_plural = _('Provision agreements')


class VersionDetail(models.Model):
    attachment_constraint = models.ForeignKey(
        'registry.AttachmentConstraint',
        on_delete=models.CASCADE,
        null=True
    )
    content_constraint = models.ForeignKey(
        'registry.ContentConstraint',
        on_delete=models.CASCADE,
        null=True
    )
    data_structure = models.ForeignKey(
        'datastructure.DataStructure',
        on_delete=models.CASCADE,
        null=True
    )
    dataflow = models.ForeignKey(
        'datastructure.Dataflow',
        on_delete=models.CASCADE,
        null=True
    )
    provision_agreement = models.ForeignKey(
        'registry.ProvisionAgreement',
        on_delete=models.CASCADE,
        null=True
    )
    version = VersionField(_('Version'))

    class Meta:
        abstract = True


class AttachmentConstraint(common.AbstractMaintainable):
    data_structures = models.ManyToManyField(
        'datastructure.DataStructure',
        verbose_name=_('Data structures'),
        through='registry.VersionDetail'
    )

    class Meta(common.AbstractMaintainable.Meta):
        abstract = True
        verbose_name = _('Attachment constraint')
        verbose_name_plural = _('Attachment constraints')


class ContentConstraint(common.AbstractMaintainable):
    

    class Type(models.IntegerChoices):
        ACTUAL = 0, _('Actual')
        ALLOWED = 1, _('Allowed')

    data_provider = models.ForeignKey(
        'base.DataProvider',
        on_delete=models.PROTECT,
        verbose_name=_('Data provider'),
        null=True,
        blank=True
    )
    data_structures = models.ManyToManyField(
        'datastructure.DataStructure',
        verbose_name=_('Data structures'),
        through='registry.VersionDetail'
    )
    dataflows = models.ManyToManyField(
        'datastructure.Dataflow',
        verbose_name=_('Dataflows'),
        through='registry.VersionDetail'
    )
    provision_agreements = models.ManyToManyField(
        'registry.ProvisionAgreement',
        verbose_name=_('Provision agreements'),
        through='registry.VersionDetail'
    )
    periodicity = models.CharField(
        _('Release calendar periodicity'),
        max_length=TINY,
        blank=True
    )
    offset = models.CharField(
        _('Release calendar offset'),
        max_length=TINY,
        blank=True
    )
    tolerance = models.CharField(
        _('Release calendar tolerance'),
        max_length=SMALL
    )
    start_time = models.DateTimeField(
        _('Reference period start time'),
        null=True,
        blank=True
    )
    end_time = models.DateTimeField(
        _('Reference period end time'),
        null=True,
        blank=True
    )
    tipe = models.IntegerField(
        _('type'), 
        choices=Type.choices,
        default=Type.ACTUAL
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
        'registry.TimePeriod', 
        on_delete=models.CASCADE,
        verbose_name=_('Before period'),
        related_name='+',
        null=True
    )
    after_period = models.ForeignKey(
        'registry.TimePeriod',
        on_delete=models.CASCADE,
        verbose_name=_('After period'),
        related_name='+',
        null=True
    )
    start_period = models.ForeignKey(
        'registry.TimePeriod', 
        on_delete=models.CASCADE,
        verbose_name=_('Start period'),
        related_name='+',
        null=True,
    )
    end_period = models.ForeignKey(
        'registry.TimePeriod', 
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
