# translation.py

from modeltranslation.translator import register, TranslationOptions

from . import models 

@register(models.Text)
class TextTranslatorOptions(TranslationOptions):
    fields = ('text',)
