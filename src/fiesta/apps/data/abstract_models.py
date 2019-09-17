from django.db import models

class AbstractData(models.Model):
    registration = models.ForeignKey('registry.Registration')

    class Meta:
        abstract = True
