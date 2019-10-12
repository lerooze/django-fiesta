# managers.py

from django.db import models
from django.conf import settings
from treebeard.mp_tree import MP_NodeManager

from ...settings import api_settings

class AgencyManager(MP_NodeManager):
    
    def get_or_create(self, object_id, parent):
        created = False
        try:
            obj = self.get(object_id=object_id)
        except self.model.DoesNotExist:
            obj = self.model(object_id=object_id)
            obj.save(parent)
            created = True
        return obj, created

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
