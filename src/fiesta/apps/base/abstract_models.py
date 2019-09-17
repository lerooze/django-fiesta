# abstract_models.py

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from ...settings import api_settings

from ..base.managers import ContactManager
from ..common import abstract_models as common

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH
TINY = api_settings.DEFAULT_TINY_STRING_LENGTH
LARGE = api_settings.DEFAULT_LARGE_STRING_LENGTH
REGULAR = api_settings.DEFAULT_STRING_LENGTH

class AbstractUser(AbstractUser):
    class Meta:
        abstract = True

class AbstractOrganisationScheme(common.MaintainableArtefact):
    class Meta:
        abstract = True

class AbstractOrganisation(common.ManyToManyItemWithParent):
    wrappers = models.ManyToManyField('OrganisationScheme')

    class Meta(common.ManyToManyItemWithParent.Meta):
        abstract = True
        # constraints = [
        #     models.UniqueConstraint(fields=['object_id'], name='unique_id')
        # ]
    
class AbstractContact(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    text = GenericRelation('common.Text')
    # names = GenericRelation('common.Text')
    # roles = GenericRelation('common.Text')
    # departments = GenericRelation('common.Text')

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', 'organisation']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'organisation'], name='unique_org_contact')
        ]
        

    objects = ContactManager()

    def __str__(self):
        return '%s: %s' % (self.user, self.organisation)

    def send_password_reset_email(self, request):
        from django.contrib.auth.forms import PasswordResetForm
        form = PasswordResetForm({'email': self.email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=True,
                email_template_name='registration/password_reset_email.html')

class AbstractTelephone(models.Model):
    value = models.CharField('phone', max_length=SMALL)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class AbstractFax(models.Model):
    value = models.CharField('FAX', max_length=SMALL)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class AbstractX400(models.Model):
    value = models.CharField('X400', max_length=SMALL)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class AbstractURI(models.Model):
    value = models.URLField('URI')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class AbstractEmail(models.Model):
    value = models.EmailField('email address')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    class Meta:
        abstract = True
