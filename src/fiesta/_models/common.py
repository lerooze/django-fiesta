from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from fiesta.settings import api_maxlen_settings as max_length 
from fiesta import constants

class Text (models.Model):
    lang = models.CharField(max_length=max_length.LANG, default='en',
                            choices=constants.LANGUAGES)
    text = models.CharField(max_length=max_length.NAME)
    text_type = models.CharField(max_length=max_length.DATA_TYPE,
                                 choices=constants.TEXT_TYPES, null=True,
                                 blank=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    nameable_object = GenericForeignKey()

class Annotation(models.Model):
    object_id = models.CharField('ID', max_length=max_length.OBJECT_ID,
                                 blank=True)
    annotation_title = models.CharField('title',
                                        max_length=max_length.ANNOTATION_TITLE,
                                        blank=True)
    annotation_type = models.CharField('type',
                                       max_length=max_length.ANNOTATION_TYPE,
                                       blank=True)
    annotation_url = models.URLField('URL', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    obj_id = models.PositiveIntegerField()
    annotable_object = GenericForeignKey('content_type', 'obj_id')
    annotation_text = GenericRelation(Text)

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.annotation_title, self.annotation_type)

class Format(models.Model):
    text_type = models.CharField(
        max_length=max_length.DATA_TYPE, 
        choices=constants.DATA_TYPES,
        null=True, blank=True
    )
    is_sequence = models.NullBooleanField(null=True, blank=True)
    interval = models.DecimalField(null=True, blank=True, max_digits=19,
                                   decimal_places=10)
    start_value = models.DecimalField(null=True, blank=True, max_digits=19,
                                      decimal_places=10)
    end_value = models.DecimalField(null=True, blank=True, max_digits=19,
                                    decimal_places=10)
    time_interval = models.DurationField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    min_value= models.DecimalField(null=True, blank=True, max_digits=19,
                                   decimal_places=10)
    max_value = models.DecimalField(null=True, blank=True, max_digits=19,
                                    decimal_places=10)
    decimals = models.PositiveIntegerField(null=True, blank=True)
    pattern = models.TextField(null=True, blank=True)
    is_multi_lingual = models.BooleanField(null=True, blank=True)

class Representation(models.Model):

    text_format = models.ForeignKey(Format, on_delete=models.CASCADE,
                                    null=True, blank=True,
                                    related_name='representation_text_formats')
    enumeration = models.ForeignKey('Codelist',
                                    on_delete=models.CASCADE, null=True,
                                    blank=True,
                                    related_name='enumerations')
    enumeration_format = models.ForeignKey(
        Format, on_delete=models.CASCADE, null=True, blank=True,
        related_name='representation_enumeration_formats')
