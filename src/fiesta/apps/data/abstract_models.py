# abstract_models.py

from django.db import models

from ...settings import api_settings 

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH

class AbstractData(models.Model):
    registration = models.ForeignKey('registry.Registration')

    class Meta:
        abstract = True

class AbstractDataSetAttrs(AbstractData):
    """Abstract model used to store DataSet attributes

    A concrete domain specific application must specialize this class in case
    of attributes that depend on the dataset.
    For each such attribute an appropriate django field must be created
    """

    class Meta:
        abstract = True

class GroupAttrs(AbstractData):
    """An abstract class used to store group attributes.

    For each DSD group a concrete domain specific application must subclass
    this class.

    The name of the subclass should be Group*Attrs where *=group_id

    For each attribute associated with this group an appropriate django field
    must be defined that its type depends on its representation.
    """
    class Meta:
        abstract = True

class DimensionsAttrs(AbstractData):
    """An abstract class used to store attributes that depend on dimensions.

    For each dimension or set of dimensions that attributes are attached to
    them and are not defined as a group (a correct DSD should always defined
    groups for this) a subclass should be defined.

    The name of the subclass should be Dimension_*_*_Attrs where * is the
    dimension id that attributes are attached to.

    For each attribute associated with these dimensions an appropriate django
    field must be defined that its type depends on its representation.
    """

    class Meta:
        abstract = True

class Dimensions(models.Model):
    """Used to store keyvalues of data

    For each dimension of type Dimension of the DSD a django appropriate field
    must be created with name the dimension id
    """

    class Meta:
        abstract = True

class PlainData(AbstractData):
    """Abstract model for DSD with no time or measure dimension

    Each domain specific application with no time or measure dimension should
    subclass this class and use it to store the data

    dim_key must be defined as a ForeignKey to the domain specific Dimensions
    class

    obs_value must be defined to reflect the DSD's representation of
    OBS_VALUE

    For each attribute attached to the measure an appropriate django field must
    be defined with name the attribute ID
    """

    class Meta:
        abstract = True

class TimeSeriesData(AbstractData):
    """Abstract model for DSD with time but no measure dimension

    Each domain specific application with time but no measure dimension should
    subclass this class and use it to store the data

    dim_key must be defined as a ForeignKey to the domain specific Dimensions
    class

    time_period must be defined as a django field that reflects the
    representation of the TIME_PERIOD

    obs_value must be defined to reflect the DSD's representation of
    OBS_VALUE

    For each attribute attached to the measure an appropriate django field must
    be defined with the attribute ID as name
    """

    class Meta:
        abstract = True

class MultipleMeasureData(AbstractData):
    """Abstract model for DSD with measure dimension but no time dimension

    Each domain specific application with measure dimension but no time
    dimension should subclass this class and use it to store the data

    dim_key must be defined as a ForeignKey to the domain specific Dimensions
    class

    For each measure defined in the measure dimension concept scheme a django
    field should be defined with measure id its name and an appropriate type
    that depends on the measure representation.

    For each attribute attached to the measure, appropriate django fields must
    be defined for each measure with name *__** where * is the measure id and
    ** is the attribute id 
    """

    class Meta:
        abstract = True

class PanelData(AbstractData):
    """Abstract model for DSD with measure and time dimension

    Each domain specific application with measure dimension and time
    dimension should subclass this class and use it to store the data

    dim_key must be defined as a ForeignKey to the domain specific Dimensions
    class

    time_period must be defined as a django field that reflects the
    representation of the TIME_PERIOD

    For each measure defined in the measure dimension concept scheme a django
    field should be defined with measure id its name and an appropriate type
    that depends on the measure representation.

    For each attribute attached to the measure, appropriate django fields must
    be defined for each measure with name *__** where * is the measure id and
    ** is the attribute id 
    """

    class Meta:
        abstract = True
