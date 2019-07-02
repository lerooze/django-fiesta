from modeltranslation.translator import register, TranslationOptions

from fiesta.apps.common import models

@register(models.Text)
class TextTranslatorOptions(TranslationOptions):
    fields = ('text',)
