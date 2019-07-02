from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import translation
from treebeard.mp_tree import MP_NodeManager

class TextManager(models.Manager):

    def get_polymorphic(self, polymorphic_obj, text_type=None):
        content_type = ContentType.get_for_model(polymorphic_obj)
        query_set = self.filter(
            content_type__pk=content_type.id,
            object_id=polymorphic_obj
        )
        if text_type:
            query_set = query_set.filter(text_type=text_type)
        return query_set
    
    def get_or_create(self, polymorphic_obj , text, text_type, language):
        created = False
        content_type = ContentType.get_for_model(polymorphic_obj)
        with translation.override(language):
            try:
                obj = self.get(
                    content_type=content_type,
                    object_id=polymorphic_obj,
                    text=text,
                    text_type=text_type,
                )
            except self.model.DoesNotExist:
                obj = self.objects.create(
                    content_type=content_type,
                    object_id=polymorphic_obj,
                    text=text,
                    text_type=text_type
                )
                created = True
        return obj, created

class AnnotationManager(models.Manager):

    def get_polymorphic(self, polymorphic_obj, text_type=None):
        content_type = ContentType.get_for_model(polymorphic_obj)
        return self.filter(
            content_type__pk=content_type.id,
            object_id=polymorphic_obj
        )

class ItemWithParentManager(MP_NodeManager):
    
    def get_or_create(self, object_id, wrapper, parent):
        created = False
        try:
            obj = self.get(object_id=object_id, wrapper=wrapper)
        except self.model.DoesNotExist:
            obj = self.model(object_id=object_id, wrapper=wrapper)
            obj.save(parent)
            created = True
        return obj, created

class ManyToManyItemWithParentManager(MP_NodeManager):

    def get_or_create(self, object_id, wrapper, parent):
        created = False
        try:
            obj = self.get(object_id=object_id)
        except self.model.DoesNotExist:
            obj = self.model(object_id=object_id)
            obj.save(parent)
            obj.wrappers.add(wrapper)
            obj.save()
            created = True
        return obj, created

class MaintainableManager(models.Manager):

    def reset_latest(self, created, data):
        if not created: return
        objects = self.filter(object_id=data.object_id,
                              agency__object_id=data.agency_id)
        objects = objects.exclude(version=data.version)
        for obj in objects:
            obj.latest = False
            obj.save()
