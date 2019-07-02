from django.apps import apps
from fiesta.settings import api_settings
from fiesta.apps.common.serializers import BaseMessageDataclass
from fiesta.apps.common.serializers import TextDataclass
from fiesta.core import status
from dataclasses import dataclass
from fiesta.core.dataclasses import field
from django.contrib.auth.models import AnonymousUser
from typing import Iterable

@dataclass 
class BaseContactDataclass(BaseMessageDataclass):
    class Meta:
        app = 'base'
    name: Iterable[TextDataclass] = field(namespace_key='common')
    department: Iterable[TextDataclass] = field()
    role: Iterable[TextDataclass] = field()
    telephone: Iterable[str] = field()
    fax: Iterable[str] = field()
    x400: Iterable[str] = field()
    uri: Iterable[str] = field(localname='URI')
    email: Iterable[str] = field()

@dataclass 
class ContactDataclass(BaseContactDataclass):

    @classmethod
    def generate_text(cls, model_name, contact):
        model = apps.get_model(cls._meta.app, model_name)
        queryset = model.objects.filter(contact=contact)
        for obj in queryset:
            yield obj.value

    @classmethod
    def generate(cls, obj):
        queryset = cls._meta.model.objects.filter(
            organisation=obj.organisation)
        for obj in queryset:
            name = TextDataclass.generate(obj, 'names')
            department = TextDataclass.generate(obj, 'departments')
            role = TextDataclass.generate(obj, 'roles')
            telephone = cls.generate_text('Telephone', obj) 
            fax = cls.generate_text('Fax', obj) 
            x400 = cls.generate_text('X400', obj) 
            uri = cls.generate_text('URI', obj) 
            email = cls.generate_text('Email', obj) 
            yield cls(
                name=name,
                department=department,
                role=role,
                telephone=telephone,
                fax=fax,
                x400=x400,
                uri=uri,
                email=email
            )

    def preprocess_isvalid(self):
        if not self.email:
            self._submission.update_status_message('Warning', '441')
            self._inner_stop = True

    def load_multi(self, obj, data, model_name):
        model = apps.get_model(self._meta.app, model_name)
        for value in data:
            model.objects.get_or_create(contact=obj, value=value)

    def preprocess_make_obj(self):
        if self._inner_stop: return
        username = list(self.email)[0]
        obj, _ = self._meta.model.objects.get_or_create(
            username, self.telephone, self.fax, self.x400, self.uri)
        return obj

    def postprocess_make_obj(self, obj):
        if self._new_user:
            request = self._process_context.request
            obj.send_password_reset_email(request)
        obj.save()
        return obj

@dataclass
class HeaderContactDataclass(BaseContactDataclass):
    class Meta:
        app = 'base'
        model = 'Contact'

    def preprocess_isvalid(self):
        # Checking that contact has an email
        if not self.email:
            self.append_error(
                status.FIESTA_1002_HEADER_CONTACT_EMAIL_NOT_FOUND,
            )
        username = self.email[0]

        # Checking that user is registered 
        try:
            contact = self._meta.model.objects.get(username=username)
        except self._meta.model.DoesNotExist:
            self.append_error(
                status.FIESTA_1004_CONTACT_NOT_REGISTERED,
                f'With username {username}'
            )
        else:
            # Checking that user is a member of Organisation
            if contact.organisation != self.parent:
                self.append_error(
                    status.FIESTA_1003_USER_NOT_IN_ORGANISATION,
                    f'Username {username}, organisation {self._parent_obj}'
                )
        self._obj = contact 

    def preprocess_make_obj(self):
        self._inner_stop = True
        return self._obj

@dataclass
class PartyDataclass(BaseMessageDataclass):

    class Meta:
        model = 'Organisation'

    name: Iterable[TextDataclass] = field(namespace_key='common')
    contact: Iterable[HeaderContactDataclass] = field()
    object_id: str = field(is_attribute=True, localname='id')

    def preprocess_isvalid(self):

        # Checking that receiver organisation exists
        try:
            receiver = self._meta.model.objects.get(
                object_id=self.object_id)
        except self._meta.model.Organisation.DoesNotExist:
            self.append_error(
                status.FIESTA_1001_HEADER_ORGANISATION_NOT_REGISTERED,
                f'[organisation id {self.object_id}]'
            )
            receiver = None
        self._obj = receiver 

    def preprocess_make_obj(self):
        return self._obj

    def wsrest_party(self, registration):
        if isinstance(registration.user, AnonymousUser):
            self.object_id='not_supplied'
            return
        contact = HeaderContactDataclass(email=[registration.user.username])
        receiver = registration.user.contact.organisation
        self.object_id = receiver.object_id
        self.contact = [contact]

@dataclass
class SenderDataclass(PartyDataclass):
    timezone: str = field()

    def preprocess_isvalid(self):
        # Checking that user is a member of Organisation
        request = self._process_context.request
        sender = self._meta.model.objects.get(
            object_id=self.object_id)
        if request.user.contact.organisation != sender:
            self.append_error(
                status.FIESTA_1003_USER_NOT_IN_ORGANISATION,
                f'[user: {self.request.user}, organisation: {sender}'
            )
        else:
            self._obj = sender

    def preprocess_make_obj(self):
        return self._obj

    def wsrest_sender(self):
        self.object_id = api_settings.DEFAULT_SENDER_ID 
