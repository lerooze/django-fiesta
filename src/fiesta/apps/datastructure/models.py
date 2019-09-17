# models.py

from .abstract_models import (
    AbstractDataStructure, AbstractDimensionList, AbstractGroup,
    AbstractAttributeList, AbstractMeasureList, AbstractDimension,
    AbstractGroupDimension, AbstractPrimaryMeasure, AbstractAttribute,
    AbstractAttributeRelationship, AbstractDataflow)

from oscar.core.loading import is_model_registered

__all__ = []

if not is_model_registered('datastructure', 'DataStructure'):
    class DataStructure(AbstractDataStructure):
        pass

    __all__.append('DataStructure')

if not is_model_registered('datastructure', 'DimensionList'):
    class DimensionList(AbstractDimensionList):
        pass

    __all__.append('DimensionList')
    
if not is_model_registered('datastructure', 'Group'):
    class Group(AbstractGroup):
        pass

    __all__.append('Group')

if not is_model_registered('datastructure', 'AttributeList'):
    class AttributeList(AbstractAttributeList):
        pass

    __all__.append('AttributeList')

if not is_model_registered('datastructure', 'MeasureList'):
    class MeasureList(AbstractMeasureList):
        pass

    __all__.append('MeasureList')

if not is_model_registered('datastructure', 'Dimension'):
    class Dimension(AbstractDimension):
        pass

    __all__.append('Dimension')

if not is_model_registered('datastructure', 'GroupDimension'):
    class GroupDimension(AbstractGroupDimension):
        pass

    __all__.append('GroupDimension')

if not is_model_registered('datastructure', 'PrimaryMeasure'):
    class PrimaryMeasure(AbstractPrimaryMeasure):
        pass

    __all__.append('PrimaryMeasure')

if not is_model_registered('datastructure', 'Attribute'):
    class Attribute(AbstractAttribute):
        pass

    __all__.append('Attribute')

if not is_model_registered('datastructure', 'AttributeRelationship'):
    class AttributeRelationship(AbstractAttributeRelationship):
        pass

    __all__.append('AttributeRelationship')

if not is_model_registered('datastructure', 'Dataflow'):
    class Dataflow(AbstractDataflow):
        pass

    __all__.append('Dataflow')
