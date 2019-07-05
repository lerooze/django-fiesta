
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from fiesta.settings import api_settings
from fiesta.apps.base.models.managers import ContactManager
from fiesta.apps.common.models import abstract

SMALL = api_settings.DEFAULT_SMALL_STRING_LENGTH
TINY = api_settings.DEFAULT_TINY_STRING_LENGTH
LARGE = api_settings.DEFAULT_LARGE_STRING_LENGTH
REGULAR = api_settings.DEFAULT_STRING_LENGTH

class AbstractUser(AbstractUser):
    class Meta:
        abstract = True

class AbstractOrganisationScheme(abstract.MaintainableArtefact):
    class Meta:
        abstract = True

class AbstractOrganisation(abstract.ManyToManyItemWithParent):
    wrappers = models.ManyToManyField('OrganisationScheme', blank=True,
                                      related_name='organisations')

    class Meta(abstract.ManyToManyItemWithParent.Meta):
        abstract = True
    
class AbstractContact(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE,
                                     related_name='organisation_contacts')
    names = GenericRelation('common.Text')
    roles = GenericRelation('common.Text')
    departments = GenericRelation('common.Text')

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['organisation']),
            models.Index(fields=['user', 'organisation']),
        ]
        unique_together = ('user', 'organisation')

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
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE,
                                related_name='telephones')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class AbstractFax(models.Model):
    value = models.CharField('FAX', max_length=SMALL)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE,
                                related_name='faxes')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class AbstractX400(models.Model):
    value = models.CharField('X400', max_length=SMALL)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE,
                                related_name='x400s')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class AbstractURI(models.Model):
    value = models.URLField('URI')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE,
                                related_name='uris')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']

class AbstractEmail(models.Model):
    value = models.EmailField('email address')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE,
                                related_name='emails')

    class Meta:
        abstract = True
        unique_together = ['contact', 'value']
