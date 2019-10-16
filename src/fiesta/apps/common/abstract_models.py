# abstract_models.py

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from model_utils import Choices
from treebeard.mp_tree import MP_Node

from ...settings import api_settings 
from ...core.validators import re_validators, errors

from . import managers

VERY_SMALL = api_settings.DEFAULT_VERY_SMALL_STRING
SMALL = api_settings.DEFAULT_SMALL_STRING
MEDIUM = api_settings.DEFAULT_MEDIUM_STRING
VERY_LARGE = api_settings.DEFAULT_VERY_LARGE_STRING

class SmallString(models.Model):
    text = models.CharField(
        max_length=SMALL,
        unique=True,
    )

    class Meta:
        abstract = True

class URLString(models.Model):
    text = models.URLField(
        _('URL'),
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('URL')
        verbose_name_plural = _('URLs')

class EmailString(models.Model):
    text = models.EmailField(
        _('Email'),
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')

class Annotation(models.Model):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        blank=True
    )
    annotation_title = models.CharField(
        _('title'), 
        max_length=MEDIUM,
        blank=True
    )
    annotation_type = models.CharField(
        _('type'), 
        max_length=VERY_SMALL, 
        blank=True
    )
    annotation_url = models.URLField(
        _('URL'), 
        blank=True
    )
    text = models.TextField(_('Text'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Annotation')
        verbose_name_plural = _('Annotations')

    def __str__(self):
        return '%s:%s:%s' % (self.object_id, self.annotation_title, self.annotation_type)

class AbstractAnnotable(models.Model):
    annotations = models.ManyToManyField(
        'common.Annotation',
        verbose_name=_('Annotations'),
        related_name='+',
    )
    class Meta:
        abstract = True

class AbstractIdentifiable(AbstractAnnotable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractNCNameIdentifiable(AbstractAnnotable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractNestedNCNameIdentifiable(AbstractAnnotable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractNameable(AbstractIdentifiable):
    name = models.CharField(
        _('Name'),
        max_length=MEDIUM,
        blank=True
    )
    description = models.CharField(
        _('Description'),
        max_length=VERY_LARGE,
        blank=True
    )

    class Meta:
        abstract = True

class AbstractNCNameNameable(AbstractNCNameIdentifiable):
    name = models.CharField(
        _('Name'),
        max_length=MEDIUM,
        blank=True
    )
    description = models.CharField(
        _('Description'),
        max_length=VERY_LARGE,
        blank=True
    )

    class Meta:
        abstract = True

class AbstractNestedNCNameNameable(AbstractNestedNCNameIdentifiable):
    name = models.CharField(
        _('Name'),
        max_length=MEDIUM,
        blank=True
    )
    description = models.CharField(
        _('Description'),
        max_length=VERY_LARGE,
        blank=True
    )

    class Meta:
        abstract = True

class AbstractVersionable(AbstractNameable):
    major = models.IntegerField(
        _('Major version'), 
        default=1, 
        db_index=True
    )
    minor = models.IntegerField(
        _('Minor version'), 
        default=0, 
        db_index=True
    )
    patch = models.IntegerField(
        _('Patch version'), 
        null=True, 
        db_index=True
    )
    valid_from = models.DateTimeField(
        _('Valid from'),
        null=True,
        blank=True)
    valid_to = models.DateTimeField(
        _('Valid to'),
        null=True,
        blank=True)

    class Meta:
        abstract = True

class AbstractNCNameVersionable(AbstractNCNameNameable, AbstractVersionable):

    class Meta:
        abstract = True

class AbstractNestedNCNameVersionable(AbstractNestedNCNameNameable, AbstractVersionable):

    class Meta:
        abstract = True

class AbstractMaintainable(AbstractVersionable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        db_index=True
    )
    agency = models.ForeignKey(
        'base.Agency', 
        verbose_name=_('Agency'), 
        on_delete=models.PROTECT
    ) 
    is_final = models.BooleanField(
        _('Is final'), 
        default=False
    )
    submitted_structure = models.ManyToManyField(
        'registry.SubmittedStructure',
        verbose_name=_('Submitted structures')
    )

    class Meta:
        abstract = True
        ordering = ['agency', 'object_id', '-major', '-minor', '-patch']
        constraints = [
            models.UniqueConstraint(
                fields=['agency', 'object_id', 'major', 'minor', 'patch'],
                name='unique_maintainable'
            )
        ]
        indexes = [
            models.Index(fields=['agency','object_id', 'major', 'minor', 'patch']),
        ]

    def __str__(self):
        return f'{self.label}={self.agency}:{self.object_id}(self.version)'

    @property
    def label(self):
        return self.__class__._meta.label

    @property
    def version(self):
        version = f'{self.major}.{self.minor}'
        if self.patch: version = f'{version}.{self.patch}'
        return version

class AbstractNCNameMaintainable(AbstractMaintainable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True
    )

    class Meta(AbstractMaintainable.Meta):
        abstract = True

class AbstractNestedNCNameMaintainable(AbstractMaintainable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        db_index=True
    )

    class Meta(AbstractMaintainable.Meta):
        abstract = True

class AbstractItem(AbstractNameable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        db_index=True
    )

    objects = managers.ItemManager()

    class Meta:
        abstract = True
        ordering = ['container', 'object_id']
        constraints = [
            models.UniqueConstraint(
                fields=['container', 'object_id'],
                name='unique_item'
            )
        ]
        indexes = [
            models.Index(fields=['container','object_id']),
        ]

    def __str__(self):
        return f'{self.label}={self.container.agency}:{self.container.object_id}(self.container.version).{self.object_id}'

    @property
    def label(self):
        return self.__class__._meta.label

class AbstractNCNameItem(AbstractItem):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True
    )

    class Meta(AbstractItem.Meta):
        abstract = True

class AbstractNestedNCNameItem(AbstractItem):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        db_index=True
    )

    class Meta(AbstractItem.Meta):
        abstract = True

class AbstractItemWithParent(AbstractItem, MP_Node):

    objects = managers.ItemWithParentManager()

    class Meta(AbstractItem.Meta):
        abstract = True

    def clean(self):
        parent = self.get_parent()
        if parent:
            if not self.container == parent.container:
                raise ValidationError({
                    'parent': errors['parent'],
                })

    def save(self, parent=None, **kwargs):
        if not self.depth:
            if parent:
                self.depth = parent.depth + 1
                parent.add_child(instance=self)
            else:
                self.add_root(instance=self)
            return  #add_root and add_child save as well
        super().save(**kwargs)

class AbstractNCNameItemWithParent(AbstractItemWithParent):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True
    )

    class Meta(AbstractItem.Meta):
        abstract = True

class AbstractNestedNCNameItemWithParent(AbstractItemWithParent):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        db_index=True
    )

    class Meta(AbstractItem.Meta):
        abstract = True

class AbstractNestedNCNameUniqueIdentifiableWithParent(AbstractIdentifiable):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ['object_id']

    def save(self, parent=None, **kwargs):
        if not self.depth:
            if parent:
                self.depth = parent.depth + 1
                parent.add_child(instance=self)
            else:
                self.add_root(instance=self)
            return  #add_root and add_child save as well
        super().save(**kwargs)

class AbstractReference(models.Model):
    agency = models.ForeignKey(
        'base.Agency',
        on_delete=models.PROTECT,
        verbose_name=_('Agency')
    )
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True
    )
    major_version = models.IntegerField(
        _('Major version'), 
        default=1, 
        db_index=True
    )
    minor_version = models.IntegerField(
        _('Minor version'), 
        default=0, 
        db_index=True
    )
    patch_version = models.IntegerField(
        _('Patch version'), 
        null=True, 
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractItemReference(AbstractReference):
    item_object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractNCNameItemReference(AbstractReference):
    item_object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        db_index=True
    )

    class Meta:
        abstract = True

class AbstractNestedNCNameItemReference(AbstractReference):
    item_object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NestedNCNameIDType']],
        db_index=True
    )

    class Meta:
        abstract = True



class Format(models.Model):
    DATA_TYPE_CHOICES = Choices( 
        (0, 'STRING', 'String'),
        (1, 'ALPHA', 'Alpha'),
        (2, 'ALPHANUMERIC', 'AlphaNumeric'),
        (3, 'NUMERIC', 'Numeric'),
        (4, 'BIGINTEGER', 'BigInteger'),
        (5, 'INTEGER', 'Integer'),
        (6, 'LONG', 'Long'),
        (7, 'SHORT', 'Short'),
        (8, 'DECIMAL', 'Decimal'),
        (9, 'FLOAT', 'Float'),
        (10, 'DOUBLE', 'Double'),
        (11, 'BOOLEAN', 'Boolean'),
        (12, 'URI', 'URI'),
        (13, 'COUNT', 'Count'),
        (14, 'INCLUSIVEVALUERANGE', 'InclusiveValueRange'),
        (15, 'EXCLUSIVEVALUERANGE', 'ExclusiveValueRange'),
        (16, 'INCREMENTAL', 'Incremental'),
        (17, 'OBSERVATIONALTIMEPERIOD', 'ObservationalTimePeriod'),
        (18, 'STANDARDTIMEPERIOD', 'StandardTimePeriod'),
        (19, 'BASICTIMEPERIOD', 'BasicTimePeriod'),
        (20, 'GREGORIANTIMEPERIOD', 'GregorianTimePeriod'),
        (21, 'GREGORIANYEAR', 'GregorianYear'),
        (22, 'GREGORIANYEARMONTH', 'GregorianYearMonth'),
        (23, 'GREGORIANDAY', 'GregorianDay'),
        (24, 'REPORTINGTIMEPERIOD', 'ReportingTimePeriod'),
        (25, 'REPORTINGYEAR', 'ReportingYear'),
        (26, 'REPORTINGSEMESTER', 'ReportingSemester'),
        (27, 'REPORTINGTRIMESTER', 'ReportingTrimester'),
        (28, 'REPORTINGQUARTER', 'ReportingQuarter'),
        (29, 'REPORTINGMONTH', 'ReportingMonth'),
        (30, 'REPORTINGWEEK', 'ReportingWeek'),
        (31, 'REPORTINGDAY', 'ReportingDay'),
        (32, 'DATETIME', 'DateTime'),
        (33, 'TIMERANGE', 'TimeRange'),
        (34, 'MONTH', 'Month'),
        (35, 'MONTHDAY', 'MonthDay'),
        (36, 'DAY', 'Day'),
        (37, 'TIME', 'Time'),
        (38, 'DURATION', 'Duration'),
    )
    text_type = models.IntegerField(
        _('Text type'),
        choices=DATA_TYPE_CHOICES,
        default=DATA_TYPE_CHOICES.STRING
    )
    is_sequence = models.BooleanField(
        _('Is sequence'), 
        null=True, 
        blank=True
    )
    interval = models.DecimalField(
        _('Interval'),
        null=True, 
        blank=True,
        max_digits=19, 
        decimal_places=10
    )
    start_value = models.DecimalField(
        _('Start value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10
    )
    end_value = models.DecimalField(
        _('End value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10
    )
    time_interval = models.DurationField(
        _('Time interval'),
        null=True, 
        blank=True
    )
    start_time = models.DateTimeField(
        _('Start time'),
        null=True, 
        blank=True
    )
    end_time = models.DateTimeField(
        _('End time'),
        null=True, blank=True
    )
    min_length = models.PositiveIntegerField(
        _('Minimum length'),
        null=True, 
        blank=True
    )
    max_length = models.PositiveIntegerField(
        _('Maximum length'), 
        null=True, 
        blank=True
    )
    min_value= models.DecimalField(
        _('Minimum value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10
    )
    max_value = models.DecimalField(
        _('Maximum value'),
        null=True, 
        blank=True, 
        max_digits=19, 
        decimal_places=10
    )
    decimals = models.PositiveIntegerField(
        _('Decimals'),
        null=True, 
        blank=True
    )
    pattern = models.TextField(
        _('Pattern'),
        null=True, 
        blank=True
    )
    is_multi_lingual = models.BooleanField(
        _('Is multi lingual'),
        null=True, 
        blank=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')

    def __str__(self):
        dic_value = {field_name: str(getattr(self, field_name, None)) for field_name in self.field_names
                     if getattr(self, field_name, None)}
        return str(dic_value)

    @cached_property
    @classmethod
    def field_names(cls):
        return [f.name for f in cls._meta.get_fields()]

class Representation(models.Model):

    text_format = models.ForeignKey(
        'common.Format', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='+', 
        verbose_name=_('Text format')
    )
    enumeration = models.ForeignKey(
        'codelist.CodelistReference',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Codelist reference')
    )
    enumeration_format = models.ForeignKey(
        'common.Format', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='+',
        verbose_name=_('Enumeration format')
    )

    def __str__(self):
        if self.text_format:
            return f'text_format: {self.text_format}'
        if not self.enumeration_format:
            return f'enumeration: {self.enumeration}'
        return f'enumeration: {self.enumeration}, enumeration_format: {self.enumeration_format}'

    class Meta:
        abstract = True
        verbose_name = _('Representation')
        verbose_name_plural = _('Representations')

class AbstractComponent(AbstractNCNameIdentifiable):

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['container', 'concept_identity', 'object_id'],
                name='unique_component'
            )
        ]
        indexes = [
            models.Index(fields=['container', 'concept_identity', 'object_id']),
        ]

class ReferencePeriod(models.Model):
    start_time = models.DateTimeField(
        _('Start time')
    )
    end_time = models.DateTimeField(
        _('End time')
    )

    class Meta:
        abstract = True
        verbose_name = _('Reference period')
        verbose_name_plural = _('Reference periods')

    def __str__(self):
        return f'{self.start_time}-{self.end_time}'

class AbstractContact(models.Model):
    name = models.CharField(
        max_length=SMALL,
        verbose_name=_('Name'))
    department = models.CharField(
        max_length=SMALL,
        verbose_name=_('Department'))
    role = models.CharField(
        max_length=SMALL,
        verbose_name=_('Role'))

    class Meta:
        abstract = True
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

class AbstractTelephone(models.Model):
    telephone = models.CharField(
        _('Telephone'),
        max_length=SMALL,
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Telephone')
        verbose_name_plural = _('Telephones')

class AbstractFax(models.Model):
    fax = models.CharField(
        _('Fax'),
        max_length=SMALL,
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Fax')
        verbose_name_plural = _('Faxes')

class AbstractX400(models.Model):
    x400 = models.CharField(
        _('X400'),
        max_length=SMALL,
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('X400')
        verbose_name_plural = _('X400s')

class AbstractEmail(models.Model):
    email = models.EmailField(
        _('Email'),
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')

class AbstractURI(models.Model):
    uri = models.URLField(
        _('URI'),
        db_index=True
    )

    class Meta:
        abstract = True
        verbose_name = _('URI')
        verbose_name_plural = _('URIs')
