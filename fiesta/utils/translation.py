from django.conf import settings

# LANGUAGE_CODE = 'en-us'
# LANGUAGES = [

def get_language(language_request):
    if language_request and language_request not in settings.LANGUAGES:
        return settings.LANGUAGE_CODE.split('-')[0]
    return language_request.split('-')[0]
