# translation.py

from modeltranslation.translator import translator

from ..common.translation import NameableTranslation

from .models import Codelist, Code

translator.register([Codelist, Code], NameableTranslation)
