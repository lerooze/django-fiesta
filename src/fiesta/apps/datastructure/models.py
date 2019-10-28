# models.py

from .abstract_models import (
    Annotation, DataStructureReference, DataStructure, DimensionList, Group,
    AttributeList, MeasureList, Dimension, GroupDimension, PrimaryMeasure,
    Attribute, AttributeRelationship, DataflowReference, Dataflow
)

from ...core.loading import is_model_registered

__all__ = []

if not is_model_registered('datastructure', 'Annotation'):
    class Annotation(Annotation):
        pass

    __all__.append('Annotation')

if not is_model_registered('datastructure', 'DataStructureReference'):
    class DataStructureReference(DataStructureReference):
        pass

    __all__.append('DataStructureReference')

if not is_model_registered('datastructure', 'DataStructure'):
    class DataStructure(DataStructure):
        pass

    __all__.append('DataStructure')

if not is_model_registered('datastructure', 'DimensionList'):
    class DimensionList(DimensionList):
        pass

    __all__.append('DimensionList')
    
if not is_model_registered('datastructure', 'Group'):
    class Group(Group):
        pass

    __all__.append('Group')

if not is_model_registered('datastructure', 'AttributeList'):
    class AttributeList(AttributeList):
        pass

    __all__.append('AttributeList')

if not is_model_registered('datastructure', 'MeasureList'):
    class MeasureList(MeasureList):
        pass

    __all__.append('MeasureList')

if not is_model_registered('datastructure', 'Dimension'):
    class Dimension(Dimension):
        pass

    __all__.append('Dimension')

if not is_model_registered('datastructure', 'GroupDimension'):
    class GroupDimension(GroupDimension):
        pass

    __all__.append('GroupDimension')

if not is_model_registered('datastructure', 'PrimaryMeasure'):
    class PrimaryMeasure(PrimaryMeasure):
        pass

    __all__.append('PrimaryMeasure')

if not is_model_registered('datastructure', 'Attribute'):
    class Attribute(Attribute):
        pass

    __all__.append('Attribute')

if not is_model_registered('datastructure', 'AttributeRelationship'):
    class AttributeRelationship(AttributeRelationship):
        pass

    __all__.append('AttributeRelationship')

if not is_model_registered('datastructure', 'DataflowReference'):
    class DataflowReference(DataflowReference):
        pass

    __all__.append('DataflowReference')

if not is_model_registered('datastructure', 'Dataflow'):
    class Dataflow(Dataflow):
        pass

    __all__.append('Dataflow')
