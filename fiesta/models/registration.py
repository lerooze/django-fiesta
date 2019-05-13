
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ..settings import api_maxlen_settings as max_length 
from ..constants import ACTIONS, STATUSES 
from ..validators import re_validators

class Submission(models.Model):
    object_id = models.CharField('ID', max_length=max_length.OBJECT_ID,
                               validators=[re_validators['IDType']])
    test = models.BooleanField(default=False)
    prepared = models.DateTimeField(null=True, blank=True)
    sender = models.ForeignKey('Organisation', on_delete=models.CASCADE,
                               related_name='sender_submissions')
    receiver = models.ForeignKey('Organisation', on_delete=models.CASCADE,
                               related_name='receiver_submissions', default=1)
    sender_contacts = models.ManyToManyField('Contact',
                                             related_name='sender_contact_submissions',)
    receiver_contacts = models.ManyToManyField('Contact',
                                               related_name='receiver_contact_submissions',)
    # channel = models.CharField(max_length=max_length.ID_CODE, choices=CHANNELS,
    #                           default='R')
    time_received = models.DateTimeField()
    time_updated = models.DateTimeField(null=True)
    status = models.CharField(max_length=max_length.OBJECT_ID, choices=STATUSES,
                             default='P')

    def __str__(self):
        return f'Submittion by {self.sender.object_id} to {self.receiver.object_id}' 

class Structure(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE,
                                   related_name='structure_submission')
    action = models.CharField(max_length=max_length.OBJECT_ID, choices=ACTIONS, default='A')
    structure_location = models.URLField(null=True)
    external_dependencies = models.BooleanField(default=False)

class SubmittedStructure(models.Model):
    structure_submission = models.ForeignKey(Structure,
                                      on_delete=models.CASCADE,
                                      related_name='submitted_structures')
    action = models.CharField(max_length=max_length.OBJECT_ID, choices=ACTIONS,
                              blank=True, null=True)
    external_dependencies = models.BooleanField(blank=True, null=True)
    status_message = models.OneToOneField('StatusMessage', null=True,
                                          on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    maintainable_object = GenericForeignKey()

# class Registration(models.Model):
#     submission = models.ForeignKey(Submission, on_delete=models.CASCADE,
#                                    related_name='registrations')
#     action = models.CharField(max_length=max_length.ID_CODE, choices=ACTIONS, default='A')
#     provision_agreement = models.ForeignKey('ProvisionAgreement',
#                                             on_delete=models.CASCADE,
#                                             related_name='registrations')
#     data_source = models.ForeignKey('Datasource', on_delete=models.CASCADE,
#                                     related_name='registrations')
#     id_code = models.CharField('ID', max_length=max_length.ID_CODE,
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

class StatusMessage(models.Model):
    status = models.CharField(max_length=max_length.OBJECT_ID, choices=STATUSES)
    message_text = models.ManyToManyField('MessageText',
                                          related_name='statuses')

class MessageText(models.Model):
    code = models.CharField('ID', max_length=max_length.OBJECT_ID,
                               validators=[re_validators['IDType']], null=True,
                           blank=True)
    text = GenericRelation('Text')

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

class WSRestStructureRequestRegistration(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    prepared = models.DateTimeField(auto_now=True)
    requester = models.ForeignKey(
        User, 
        related_name='wsrest_structure_requests',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    resource = models.CharField(max_length=max_length.OBJECT_ID)
    agency_id = models.CharField(max_length=max_length.OBJECT_ID)
    resource_id = models.CharField(max_length=max_length.OBJECT_ID)
    version = models.CharField(max_length=max_length.OBJECT_ID)
    detail = models.CharField(max_length=max_length.OBJECT_ID)
    references = models.CharField(max_length=max_length.OBJECT_ID)
