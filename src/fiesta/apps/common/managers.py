# managers.py

from django.apps import apps
from django.db import models
from treebeard.mp_tree import MP_NodeManager

from ...core import status 

class ItemManager(models.Manager):

    def get_from_ref(self, ref):
        try:
            return self.get(object_id=ref.object_id) 
        except self.model.DoesNotExist:
            ref._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2407_ITEM_NOT_REGISTERED,
            )
            ref._stop = True

class ItemWithParentManager(MP_NodeManager):
    
    def get_from_ref(self, ref):
        try:
            return self.get(object_id=ref.object_id) 
        except self.model.DoesNotExist:
            ref._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2407_ITEM_NOT_REGISTERED,
            )
            ref._stop = True

    def get_or_create(self, object_id, wrapper, parent):
        created = False
        try:
            obj = self.get(object_id=object_id)
        except self.model.DoesNotExist:
            obj = self.model(object_id=object_id)
            obj.save(parent)
            obj.containers.add(wrapper)
            created = True
        return obj, created

class MaintainableManager(models.Manager):

    def get_version(self, version):
        version_tuple = version.split('.')
        if len(version_tuple) == 2:
            version_tuple.append(None)
        return version_tuple

    def get_from_ref(self, ref):
        agency_model = apps.get_model('base','agency')
        if ref.maintainable_parent_id:
            agency_id = ref.maintainable_parent_id
            object_id = ref.container_id
            version = ref.maintainable_parent_version
        else:
            agency_id = ref.agency_id
            object_id = ref.object_id
            version = ref.version
        version = self.get_version(version)
        package = ref.package
        try:
            agency = agency_model.objects.get(object_id=agency_id)
        except agency_model.DoesNotExist:
            ref._context.result.status_message.update(
                'Failure', 
                status.FIESTA_2403_AGENCY_NOT_REGISTERED,
            )
            ref._stop = True
        else:
            try:
                maintainable = self.get(object_id=object_id, agency=agency)
            except self.model.DoesNotExist:
                # If an AttachmentConstraint reference create instance since
                # DSDs are created before AttachmentConstraints are processed
                if ref.cls == 'AttachmentConstraint':
                    maintainable = self.create(object_id=object_id, agency=agency)
                else:
                    ref._context.result.status_message.update(
                        'Failure', 
                        status.FIESTA_2406_MAINTAINABLE_ARTEFACT_INEXISTENT,
                    )
                    ref._stop = True
                    return
            versionable_model = apps.get_model(package, 'versionable')
            kwargs = {
                maintainable._meta.name: maintainable,
                'major': version[0],
                'minor': version[1],
                'patch': version[2]
            }
            versionable = versionable_model.objects.get(**kwargs)
            return versionable
