
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from fiesta.settings import api_settings
from fiesta.core import constants
from fiesta.core.validators import re_validators

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH
TINY = api_settings.DEFAULT_TINY_STRING_LENGTH
LARGE = api_settings.DEFAULT_LARGE_STRING_LENGTH
REGULAR = api_settings.DEFAULT_STRING_LENGTH


class AbstractLog(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel = models.CharField(max_length=SMALL, choices=constants.CHANNELS)
    created = models.DateTimeField(auto_now_add=True)
    progress = models.CharField(max_length=SMALL, choices=constants.PROGRESS,
                              default='Processing', editable=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def update_progress(self, status):
        self.progress = status
        self.save()

class AbstractAcquisitionLog(AbstractLog):
    acquisition_file = models.FileField(upload_to='%Y/%m/%d/')
    acquisition_report = models.FileField(upload_to='%Y/%m/%d/', editable=False)

    class Meta:
        abstract = True


class AbstractQueryLog(AbstractLog):
    query_file = models.FileField(upload_to='%Y/%m/%d/')
    query_report = models.FileField(upload_to='%Y/%m/%d/', editable=False)

    class Meta:
        abstract = True

class AbstractSubmission(models.Model):
    log = models.OneToOneField('AcquisitionLog', on_delete=models.CASCADE,
                                   related_name='submission')
    object_id = models.CharField('ID', max_length=SMALL,
                                 validators=[re_validators['IDType']],
                                 editable=False)
    test = models.BooleanField(default=False)
    prepared = models.DateTimeField(null=True, blank=True, editable=False)
    sender = models.ForeignKey('base.Organisation', on_delete=models.CASCADE,
                               related_name='sender_submissions',
                               editable=False)
    receiver = models.ForeignKey('base.Organisation', on_delete=models.CASCADE,
                                 related_name='receiver_submissions',
                                 editable=False)
    sender_contacts = models.ManyToManyField('base.Contact',
                                             related_name='sender_contact_submissions',
                                             editable=False)
    receiver_contacts = models.ManyToManyField('base.Contact',
                                               related_name='receiver_contact_submissions',
                                               editable=False)

    def __str__(self):
        return f'Submittion by {self.sender.object_id} to {self.receiver.object_id}'

    class Meta:
        abstract = True

class AbstractSubmitStructureRequest(models.Model):
    submission = models.OneToOneField('Submission', on_delete=models.CASCADE,
                                      related_name='submit_structure_request')
    action = models.CharField(max_length=SMALL, choices=constants.ACTIONS, default='A')
    structure_location = models.URLField(null=True)
    external_dependencies = models.BooleanField(default=False)

    class Meta:
        abstract = True

class AbstractSubmittedStructure(models.Model):
    structure_submission = models.ForeignKey('Structure',
                                             on_delete=models.CASCADE,
                                             related_name='submitted_structures')
    action = models.CharField(max_length=SMALL, choices=constants.ACTIONS,
                              blank=True, null=True)
    external_dependencies = models.BooleanField(blank=True, null=True)
    status_message = models.OneToOneField('StatusMessage', null=True,
                                          on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    maintainable_object = GenericForeignKey()

    class Meta:
        abstract = True

# class AbstractRegistration(models.Model):
#     submission = models.ForeignKey('Submission', on_delete=models.CASCADE,
#                                    related_name='registrations')
#     action = models.CharField(max_length=SMALL, choices=constants.ACTIONS, default='A')
#     provision_agreement = models.ForeignKey('ProvisionAgreement',
#                                             on_delete=models.CASCADE,
#                                             related_name='registrations')
#     data_source = models.ForeignKey('Datasource', on_delete=models.CASCADE,
#                                     related_name='registrations')
#     id_code = models.CharField('ID', max_length=SMALL,
#                                validators=[re_validators['IDType']])
#     valid_from = models.DateTimeField(null=True, blank=True)
#     valid_to = models.DateTimeField(null=True, blank=True)
#     last_updated = models.DateTimeField(null=True, blank=True)
#     index_time_series = models.BooleanField(default=False)
#     index_data_set= models.BooleanField(default=False)
#     index_attributes = models.BooleanField(default=False)
#     index_reporting_period = models.BooleanField(default=False)
#     status_message = models.OneToOneField('StatusMessage', null=True)
#
#     def __str__(self):
#         return '%s:%s:%s' % (self.registrant.username, self.action, self.interactive)
#
#     def save(self, **kwargs):
#         if not self.depth:
#             if self.parent_id:
#                 self.depth = self.parent.depth + 1
#                 self.parent.add_child(instance=self)
#             else:
#                 self.add_root(instance=self)
#             return  #add_root and add_child save as well
#         super().save(**kwargs)
#
#     class Meta:
#         abstract = True

class AbstractStatusMessage(models.Model):
    status = models.CharField(max_length=SMALL, choices=constants.STATUSES)
    message_text = models.ManyToManyField('StatusMessageText')

    class Meta:
        abstract = True

class AbstractStatusMessageText(models.Model):
    code = models.CharField('ID', max_length=SMALL,
                            validators=[re_validators['IDType']], null=True,
                            blank=True)
    text = GenericRelation('common.Text')

    class Meta:
        abstract = True

# class Datasource(models.Model): 
#     simple_data_source = models.URLField(blank=True, null=True)
#     queryable_data_source = models.OneToOneField('QueryableDatasource',
#                                                  null=True)
# class QueryableDatasource(models.Model):
#     data_url = models.URLField()
#     wsdl_url = models.URLField(blank=True, null=True)
#     wadl_url = models.URLField(blank=True, null=True)
#     is_rest_data_source = models.BooleanField()
#     is_web_service_data_source = models.BooleanField()

class AbstractRESTfulQuery(models.Model):
    log = models.OneToOneField('QueryLog', on_delete=models.CASCADE,
                                   related_name='restful_query')
    resource = models.CharField(max_length=SMALL)
    agency_id = models.CharField(max_length=SMALL)
    resource_id = models.CharField(max_length=SMALL)
    version = models.CharField(max_length=SMALL)
    detail = models.CharField(max_length=SMALL)
    references = models.CharField(max_length=SMALL)

    class Meta:
        abstract = True
