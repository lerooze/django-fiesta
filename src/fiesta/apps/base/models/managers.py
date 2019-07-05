
from django.db import models
from django.conf import settings
from fiesta.settings import api_settings

class ContactManager(models.Manager):

    def get_or_create(self, username, organisation, telephone, fax, x400, uri):
        created = False
        User = settings.AUTH_USER_MODEL
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            password = api_settings.DEFAULT_NEW_USER_PASSWORD 
            user = User.objects.create(
                username=username,
                email=username,
                password=password
            )
            contact = user.contact
            contact.organisation = organisation 
            created = True
        return user.contact, created

    # @staticmethod
    # def load_multi(obj, data, model_name):
    #     model = apps.get_model('base', model_name)
    #     for value in data:
    #         model.objects.get_or_create(contact=obj, value=value)

