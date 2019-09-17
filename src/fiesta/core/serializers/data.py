from .base import field
from .structure import Serializer, AnnotableArtefact, ReferenceSerializer, BaseSDMXMessageSerializer
from typing import Iterable
from datetime import datetime


class DataSetSerializer(Serializer):
    registration = RegistrationSerializer()

class GenericDataSerializer(Serializer):
    
    class Meta:
        namespace_key = 'data'

class AnnotableGenericDataSerializer(AnnotableArtefact):
    class Meta:
        namespace_key = 'data'
    
        
class AttributesSerializer(GenericDataSerializer):
    pass

class ValueSerializer(GenericDataSerializer):
    object_id: str = field(localname='id', is_attribute=True)
    value: str = field(is_attribute=True)

class ValuesSerializer(GenericDataSerializer):
    value: Iterable[ValueSerializer] = field()

class GroupSerializer(AnnotableGenericDataSerializer):
    group_key: ValuesSerializer = field()
    attributes: ValuesSerializer = field() 
    tipe: str = field(localname='type', is_attribute=True)

class ObsSerializer(AnnotableGenericDataSerializer):
    obs_dimension: ValueSerializer = field()
    obs_value: ValuesSerializer = field()
    attributes: ValuesSerializer = field()


class SeriesSerializer(AnnotableGenericDataSerializer):
    series_key: ValuesSerializer = field()
    attributes: ValuesSerializer = field()
    obs: Iterable[ObsSerializer] = field()

class ObsOnlySerializer(AnnotableGenericDataSerializer):
    obs_key: ValuesSerializer = field()
    obs_value: ValuesSerializer = field()
    attributes: ValuesSerializer = field()

class DataSetSerializer(AnnotableGenericDataSerializer):
    data_provider: ReferenceSerializer = field()
    attributes: AttributesSerializer = field()
    group: Iterable[GroupSerializer] = field()
    series: Iterable[SeriesSerializer] = field()
    obs: Iterable[ObsOnlySerializer] = field()
    structureRef: str = field(is_attribute=True)
    setID: str = field(is_attribute=True)
    action: str = field(is_attribute=True)
    reporting_begin_date: str = field(is_attribute=True)
    reporting_end_date: str = field(is_attribute=True)
    valid_from_date: datetime = field(is_attribute=True)
    valid_to_date: datetime = field(is_attribute=True)
    publication_year: int = field(is_attribute=True)
    publication_period: str = field(is_attribute=True)

class GenericDataSerializer(BaseSDMXMessageSerializer):
    data_set = DataSetSerializer()

class GenericTimeSeriesDataSerializer(GenericDataSerializer):
    pass
