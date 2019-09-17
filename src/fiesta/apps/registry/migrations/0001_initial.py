# Generated by Django 2.2.3 on 2019-09-10 04:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0001_initial'),
        ('datastructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcquisitionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(choices=[('Registry', 'Registry'), ('Upload', 'Upload'), ('Interactive', 'Interactive'), ('RESTful_query', 'RESTful_query'), ('SOAP_query', 'SOAP_query'), ('RESTful_GUI_query', 'RESTful_GUI_query'), ('SOAP_GUI_query', 'SOAP_GUI_query')], max_length=63)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('progress', models.CharField(choices=[('Finished', 'Finished'), ('Processing', 'Processing')], default='Processing', editable=False, max_length=63)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('acquisition_file', models.FileField(upload_to='%Y/%m/%d/')),
                ('acquisition_report', models.FileField(editable=False, upload_to='%Y/%m/%d/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QueryLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(choices=[('Registry', 'Registry'), ('Upload', 'Upload'), ('Interactive', 'Interactive'), ('RESTful_query', 'RESTful_query'), ('SOAP_query', 'SOAP_query'), ('RESTful_GUI_query', 'RESTful_GUI_query'), ('SOAP_GUI_query', 'SOAP_GUI_query')], max_length=63)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('progress', models.CharField(choices=[('Finished', 'Finished'), ('Processing', 'Processing')], default='Processing', editable=False, max_length=63)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StatusMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Success', 'Success'), ('Warning', 'Warning'), ('Failure', 'Failure')], max_length=63)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StatusMessageText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=63, null=True, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(editable=False, max_length=63, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('test', models.BooleanField(default=False)),
                ('prepared', models.DateTimeField(blank=True, editable=False, null=True)),
                ('log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='submission', to='registry.AcquisitionLog')),
                ('receiver', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='receiver_submissions', to='base.Organisation')),
                ('receiver_contacts', models.ManyToManyField(editable=False, related_name='receiver_contact_submissions', to='base.Contact')),
                ('sender', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='sender_submissions', to='base.Organisation')),
                ('sender_contacts', models.ManyToManyField(editable=False, related_name='sender_contact_submissions', to='base.Contact')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubmitStructureRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('Append', 'Append'), ('Replace', 'Replace'), ('Delete', 'Delete')], default='A', max_length=63)),
                ('structure_location', models.URLField(null=True)),
                ('external_dependencies', models.BooleanField(default=False)),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='submit_structure_request', to='registry.Submission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubmittedStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(blank=True, choices=[('Append', 'Append'), ('Replace', 'Replace'), ('Delete', 'Delete')], max_length=63, null=True)),
                ('external_dependencies', models.BooleanField(blank=True, null=True)),
                ('status_message', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.StatusMessage')),
                ('submit_structure_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_structures', to='registry.SubmitStructureRequest')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='statusmessage',
            name='message_text',
            field=models.ManyToManyField(to='registry.StatusMessageText'),
        ),
        migrations.CreateModel(
            name='RESTfulRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource', models.CharField(max_length=63)),
                ('agency_id', models.CharField(max_length=63)),
                ('resource_id', models.CharField(max_length=63)),
                ('version', models.CharField(max_length=63)),
                ('detail', models.CharField(max_length=63)),
                ('references', models.CharField(max_length=63)),
                ('log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='restful_query', to='registry.QueryLog')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProvisionAgreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(default='1.0', max_length=15, validators=[django.core.validators.RegexValidator(re.compile('[0-9]+(\\.[0-9]+)*'), 'Enter a value of type VersionType that has pattern "([0-9]+(\\.[0-9]+)*)"', 'invalid_pattern')], verbose_name='Version')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='Valid from')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='Valid to')),
                ('object_id', models.CharField(max_length=63, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('is_final', models.BooleanField(default=False, verbose_name='Is final')),
                ('latest', models.BooleanField(default=False)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Organisation', verbose_name='Agency')),
                ('data_provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provisionagreement_data_provider_set', related_query_name='provisionagreement_data_provider', to='base.Organisation')),
                ('dataflow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='datastructure.Dataflow')),
                ('submitted_structure', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.SubmittedStructure')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]