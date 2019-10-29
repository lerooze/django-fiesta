
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from treebeard.mp_tree import MP_Node
from versionfield import VersionField

from ...settings import api_settings 
from ...core.validators import re_validators, errors

from . import managers

VERY_SMALL = api_settings.DEFAULT_VERY_SMALL_STRING
SMALL = api_settings.DEFAULT_SMALL_STRING
MEDIUM = api_settings.DEFAULT_MEDIUM_STRING
VERY_LARGE = api_settings.DEFAULT_VERY_LARGE_STRING

class AbstractAnnotation(models.Model):
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


class AbstractIdentifiable(models.Model):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['IDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True


class AbstractNCNameIdentifiable(models.Model):
    object_id = models.CharField(
        _('ID'), 
        max_length=VERY_SMALL, 
        validators=[re_validators['NCNameIDType']],
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True


class AbstractNestedNCNameIdentifiable(models.Model):
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
    version = VersionField(default='1.0')
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
        ordering = ['agency', 'object_id', '-version']
        constraints = [
            models.UniqueConstraint(
                fields=['agency', 'object_id', 'version'],
                name='%(app_label)s_%(class)s_unique_maintainable'
            )
        ]
        indexes = [
            models.Index(fields=['agency','object_id', 'version']),
        ]

    def __str__(self):
        return f'{self.label}={self.agency}:{self.object_id}(self.version)'

    @property
    def label(self):
        return self.__class__._meta.label


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
                name='%(app_label)s_%(class)s_unique_item'
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


class Format(models.Model):
    

    class DataType(models.IntegerChoices):
        STRING = 0, _('String')
        ALPHA = 1, _('Alpha')
        ALPHANUMERIC = 2, _('AlphaNumeric')
        NUMERIC = 3, _('Numeric')
        BIGINTEGER = 4, _('Big integer')
        INTEGER = 5, _('Integer')
        LONG = 6, _('Long')
        SHORT = 7, _('Short')
        DECIMAL = 8, _('Decimal')
        FLOAT = 9, _('Float')
        DOUBLE = 10, _('Double')
        BOOLEAN = 11, _('Boolean')
        URI = 12, _('URI')
        COUNT = 13, _('Count')
        INCLUSIVEVALUERANGE = 14, _('Inclusive value range')
        EXCLUSIVEVALUERANGE = 15, _('Exclusive value range')
        INCREMENTAL = 16, _('Incremental')
        OBSERVATIONALTIMEPERIOD = 17, _('Observational time period')
        STANDARDTIMEPERIOD = 18, _('Standard time period')
        BASICTIMEPERIOD = 19, _('Basic time period')
        GREGORIANTIMEPERIOD = 20, _('Gregorian time period')
        GREGORIANYEAR = 21, _('Gregorian year')
        GREGORIANYEARMONTH = 22, _('Gregorian year month')
        GREGORIANMONTH = 23, _('Gregorian month')
        GREGORIANDAY = 24, _('Gregorian day')
        REPORTINGTIMEPERIOD = 25, _('Reporting time period')
        REPORTINGYEAR = 26, _('Reporting year')
        REPORTINGSEMESTER = 27, _('Reporting semester')
        REPORTINGTRIMESTER = 28, _('Reporting trimester')
        REPORTINGQUARTER = 29, _('Reporting quarter')
        REPORTINGMONTH = 30, _('Reporting month')
        REPORTINGWEEK = 31, _('Reporting week')
        REPORTINGDAY = 32, _('Reporting day')
        DATETIME = 33, _('Date time')
        TIMERANGE = 34, _('Time range')
        MONTH = 35, _('Month')
        MONTHDAY = 36, _('Month day')
        DAY = 37, _('Day')
        TIME = 38, _('Time')
        DURATION = 39, _('Duration')
    
    text_type = models.IntegerField(
        _('Text type'),
        choices=DataType.choices,
        default=DataType.STRING
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
        'codelist.Codelist',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Codelist reference')
    )
    enumeration_version = VersionField(
        _('Enumeration version'),
        blank=True,
        null=True
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
                name='%(app_label)s_%(class)s_unique_component'
            )
        ]
        indexes = [
            models.Index(fields=['container', 'concept_identity', 'object_id']),
        ]

    def __str__(self):
        return f'{self.start_time}-{self.end_time}'


class Contact(models.Model):
    party = models.ForeignKey(
        'registry.Party',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Party'),
        related_name='contact_set',
        related_query_name='contact',
    )
    agency = models.ForeignKey(
        'base.Agency',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Agency'),
        related_name='contact_set',
        related_query_name='contact',
    )
    data_provider = models.ForeignKey(
        'base.DataProvider',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Data provider'),
        related_name='contact_set',
        related_query_name='contact',
    )
    data_consumer = models.ForeignKey(
        'base.DataConsumer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Data consumer'),
        related_name='contact_set',
        related_query_name='contact',
    )
    organisation_unit = models.ForeignKey(
        'base.OrganisationUnit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Organisation unit'),
        related_name='contact_set',
        related_query_name='contact',
    )
    name = models.CharField(
        max_length=SMALL,
        verbose_name=_('Name'))
    department = models.CharField(
        max_length=SMALL,
        verbose_name=_('Department'))
    role = models.CharField(
        max_length=SMALL,
        verbose_name=_('Role'))
    telephone = models.CharField(
        max_length=MEDIUM,
        verbose_name=_('Telephone'))
    fax = models.CharField(
        max_length=MEDIUM,
        verbose_name=_('Fax'))
    X400 = models.CharField(
        max_length=MEDIUM,
        verbose_name=_('X400'))
    email = models.CharField(
        max_length=MEDIUM,
        verbose_name=_('Email'))
    uri = models.CharField(
        max_length=MEDIUM,
        verbose_name=_('URI'))

    class Meta:
        abstract = True
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
