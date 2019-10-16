# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation

from .models import DataStructure, Dataflow  

translator.register([DataStructure, Dataflow], NameableTranslation)
