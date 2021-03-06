# Generated by Django 3.0b1 on 2019-10-29 18:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re
import versionfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0001_initial'),
        ('datastructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentConstraint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('version', versionfield.VersionField(default='1.0')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='Valid from')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='Valid to')),
                ('object_id', models.CharField(db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('is_final', models.BooleanField(default=False, verbose_name='Is final')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Agency', verbose_name='Agency')),
            ],
            options={
                'verbose_name': 'Attachment constraint',
                'verbose_name_plural': 'Attachment constraints',
                'ordering': ['agency', 'object_id', '-version'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContentConstraint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('version', versionfield.VersionField(default='1.0')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='Valid from')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='Valid to')),
                ('object_id', models.CharField(db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('is_final', models.BooleanField(default=False, verbose_name='Is final')),
                ('periodicity', models.CharField(blank=True, max_length=15, verbose_name='Release calendar periodicity')),
                ('offset', models.CharField(blank=True, max_length=15, verbose_name='Release calendar offset')),
                ('tolerance', models.CharField(max_length=63, verbose_name='Release calendar tolerance')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Reference period start time')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='Reference period end time')),
                ('tipe', models.IntegerField(choices=[(0, 'Actual'), (1, 'Allowed')], default=0, verbose_name='type')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Agency', verbose_name='Agency')),
                ('data_provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.DataProvider', verbose_name='Data provider')),
            ],
            options={
                'verbose_name': 'Content constraint',
                'verbose_name_plural': 'Content constraints',
                'ordering': ['agency', 'object_id', '-version'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CubeRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('include', models.BooleanField(verbose_name='include')),
                ('attachment_constraint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.AttachmentConstraint', verbose_name='Attachment constraint')),
                ('content_constraint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.ContentConstraint', verbose_name='Content constraint')),
            ],
            options={
                'verbose_name': 'Cube region',
                'verbose_name_plural': 'Cube regions',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CubeRegionKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component_id', models.CharField(max_length=63, verbose_name='Component ID')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_set', related_query_name='attribute', to='registry.CubeRegion', verbose_name='Cube region')),
                ('key_value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='key_value_set', related_query_name='key_value', to='registry.CubeRegion', verbose_name='Cube region')),
            ],
            options={
                'verbose_name': 'Cube region key',
                'verbose_name_plural': 'Cube region keys',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=63, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('test', models.BooleanField(default=False, verbose_name='Test')),
                ('prepared', models.DateTimeField(blank=True, null=True, verbose_name='Prepared')),
                ('name', models.CharField(max_length=127, verbose_name='Transmission name')),
                ('name_en', models.CharField(max_length=127, null=True, verbose_name='Transmission name')),
                ('name_el', models.CharField(max_length=127, null=True, verbose_name='Transmission name')),
                ('data_set_action', models.IntegerField(blank=True, choices=[(0, 'Append'), (1, 'Replace'), (2, 'Delete'), (3, 'Information')], null=True, verbose_name='Data set action')),
                ('data_set_id', models.CharField(blank=True, max_length=63, verbose_name='Data set ID')),
                ('extracted', models.DateTimeField(auto_now=True, verbose_name='Extracted')),
                ('reporting_begin', models.CharField(blank=True, max_length=127, verbose_name='Reporting begin')),
                ('reporting_end', models.CharField(blank=True, max_length=127, verbose_name='Reporting end')),
                ('embargo_date', models.DateTimeField(blank=True, null=True, verbose_name='Embargo date')),
                ('source', models.CharField(blank=True, max_length=63, verbose_name='Source')),
                ('source_en', models.CharField(blank=True, max_length=63, null=True, verbose_name='Source')),
                ('source_el', models.CharField(blank=True, max_length=63, null=True, verbose_name='Source')),
                ('data_provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='base.DataProvider', verbose_name='Data provider')),
            ],
            options={
                'verbose_name': 'Header',
                'verbose_name_plural': 'Headers',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Key',
                'verbose_name_plural': 'Keys',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(db_index=True, max_length=63, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('timezone', models.CharField(blank=True, max_length=63)),
            ],
            options={
                'verbose_name': 'Party',
                'verbose_name_plural': 'Parties',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProvisionAgreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('version', versionfield.VersionField(default='1.0')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='Valid from')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='Valid to')),
                ('object_id', models.CharField(db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('is_final', models.BooleanField(default=False, verbose_name='Is final')),
                ('dataflow_version', versionfield.VersionField()),
                ('dataprovider_version', versionfield.VersionField()),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Agency', verbose_name='Agency')),
                ('dataflow', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registry.ProvisionAgreement', verbose_name='Provision agreement')),
                ('dataprovider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.DataProvider', verbose_name='Data provider')),
            ],
            options={
                'verbose_name': 'Provision agreement',
                'verbose_name_plural': 'Provision agreements',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StatusMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Success'), (1, 'Warning'), (2, 'Failure')], verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Status message',
                'verbose_name_plural': 'Status messages',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubmitStructureRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('structure_location', models.URLField(blank=True, null=True, verbose_name='Structure location')),
                ('action', models.IntegerField(choices=[(0, 'Append'), (1, 'Replace'), (2, 'Delete'), (3, 'Information')], default=0, verbose_name='Action')),
                ('external_dependencies', models.BooleanField(default=False, verbose_name='External dependencies')),
                ('header', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='registry.Header', verbose_name='Header')),
            ],
            options={
                'verbose_name': 'Submit structure request',
                'verbose_name_plural': 'Submit structure requests',
                'permissions': [('maintainable', 'Can perform CRUD operations on maintainable artefacts')],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_period', models.CharField(max_length=63, verbose_name='Time period')),
                ('is_inclusive', models.BooleanField(default=True, verbose_name='Is inclusive')),
            ],
            options={
                'verbose_name': 'Time period',
                'verbose_name_plural': 'Time periods',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VersionDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', versionfield.VersionField()),
                ('attachment_constraint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.AttachmentConstraint')),
                ('content_constraint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.ContentConstraint')),
                ('data_structure', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='datastructure.DataStructure')),
                ('dataflow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='datastructure.Dataflow')),
                ('provision_agreement', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.ProvisionAgreement')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubmittedStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.IntegerField(choices=[(0, 'Append'), (1, 'Replace'), (2, 'Delete'), (3, 'Information')], default=0, verbose_name='Action')),
                ('external_dependencies', models.BooleanField(blank=True, null=True, verbose_name='External dependencies')),
                ('status_message', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='registry.StatusMessage', verbose_name='Status message')),
                ('submit_structure_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registry.SubmitStructureRequest', verbose_name='Submit structure request')),
            ],
            options={
                'verbose_name': 'Submitted structure',
                'verbose_name_plural': 'Submitted structures',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component_id', models.CharField(max_length=63, verbose_name='Component ID')),
                ('value', models.CharField(blank=True, max_length=63, verbose_name='Value')),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registry.Key', verbose_name='Key')),
            ],
            options={
                'verbose_name': 'Sub key',
                'verbose_name_plural': 'Sub keys',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='provisionagreement',
            name='submitted_structure',
            field=models.ManyToManyField(to='registry.SubmittedStructure', verbose_name='Submitted structures'),
        ),
        migrations.CreateModel(
            name='PayloadStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('structure_code', models.CharField(max_length=63, verbose_name='Structure ID')),
                ('schema_url', models.URLField(blank=True, verbose_name='Schema URL')),
                ('namespace', models.CharField(blank=True, max_length=127, verbose_name='Namespace')),
                ('dimension_at_observation', models.CharField(blank=True, max_length=31, verbose_name='Observation dimension')),
                ('explicit_measures', models.BooleanField(blank=True, null=True, verbose_name='Explicit measures')),
                ('service_url', models.URLField(blank=True, null=True, verbose_name='Service URL')),
                ('structure_url', models.URLField(blank=True, null=True, verbose_name='Structure URL')),
                ('provision_agreement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='registry.ProvisionAgreement', verbose_name='Provision agreement')),
                ('structure', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='datastructure.DataStructure', verbose_name='Structure')),
                ('structure_usage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='datastructure.Dataflow', verbose_name='Structure usage')),
            ],
            options={
                'verbose_name': 'Payload structure',
                'verbose_name_plural': 'Payload structures',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.IntegerField(choices=[(0, 'UploadStructureGUI'), (1, 'UploadStructureREST'), (2, 'UploadDataGUI'), (3, 'UploadDataREST'), (4, 'RequestStructureGUI'), (5, 'RequestStructureREST'), (6, 'RequestDataGUI'), (7, 'RequestDataREST')], editable=False, verbose_name='Channel')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('progress', models.CharField(choices=[(0, 'Submitted'), (1, 'Negotiating'), (2, 'Parsing'), (3, 'Processing'), (4, 'Completed')], default=3, editable=False, max_length=63, verbose_name='Progress')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('request_file', models.FileField(editable=False, null=True, upload_to='requests/%Y/%m/%d/', verbose_name='Request file')),
                ('response_file', models.FileField(editable=False, null=True, upload_to='responses/%Y/%m/%d/', verbose_name='Response file')),
                ('exceptions_file', models.FileField(editable=False, null=True, upload_to='exceptions/%Y/%m/%d/', verbose_name='exceptions_file')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Log',
                'verbose_name_plural': 'Logs',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KeySet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_included', models.BooleanField(verbose_name='Is included')),
                ('attachment_constraint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.AttachmentConstraint', verbose_name='Attachment constraint')),
                ('content_constraint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.ContentConstraint', verbose_name='Content constraint')),
            ],
            options={
                'verbose_name': 'Key set',
                'verbose_name_plural': 'Key sets',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='key',
            name='key_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registry.KeySet', verbose_name='Key set'),
        ),
        migrations.AddField(
            model_name='header',
            name='log',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.PROTECT, to='registry.Log', verbose_name='Log'),
        ),
        migrations.AddField(
            model_name='header',
            name='receiver',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='registry.Party', verbose_name='Receiver'),
        ),
        migrations.AddField(
            model_name='header',
            name='sender',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='registry.Party', verbose_name='Sender'),
        ),
        migrations.AddField(
            model_name='header',
            name='structure',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='registry.PayloadStructure', verbose_name='Structure'),
        ),
        migrations.CreateModel(
            name='ErrorCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(choices=[], verbose_name='Error code')),
                ('status_message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registry.StatusMessage', verbose_name='Status message')),
            ],
            options={
                'verbose_name': 'Error code',
                'verbose_name_plural': 'Error codes',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CubeRegionKeyValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cascade_values', models.BooleanField(default=False, verbose_name='Cascade values')),
                ('value', models.CharField(blank=True, max_length=63, verbose_name='Value')),
                ('cube_region_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.CubeRegionKey', verbose_name='Cube region key')),
            ],
            options={
                'verbose_name': 'Cube region key value',
                'verbose_name_plural': 'Cube region key values',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CubeRegionKeyTimeRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('after_period', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='registry.TimePeriod', verbose_name='After period')),
                ('before_period', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='registry.TimePeriod', verbose_name='Before period')),
                ('cube_region_key', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.CubeRegionKey', verbose_name='Cube region key')),
                ('end_period', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='registry.TimePeriod', verbose_name='End period')),
                ('start_period', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='registry.TimePeriod', verbose_name='Start period')),
            ],
            options={
                'verbose_name': 'Cube region key time range',
                'verbose_name_plural': 'Cube region key time ranges',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='contentconstraint',
            name='data_structures',
            field=models.ManyToManyField(through='registry.VersionDetail', to='datastructure.DataStructure', verbose_name='Data structures'),
        ),
        migrations.AddField(
            model_name='contentconstraint',
            name='dataflows',
            field=models.ManyToManyField(through='registry.VersionDetail', to='datastructure.Dataflow', verbose_name='Dataflows'),
        ),
        migrations.AddField(
            model_name='contentconstraint',
            name='provision_agreements',
            field=models.ManyToManyField(through='registry.VersionDetail', to='registry.ProvisionAgreement', verbose_name='Provision agreements'),
        ),
        migrations.AddField(
            model_name='contentconstraint',
            name='submitted_structure',
            field=models.ManyToManyField(to='registry.SubmittedStructure', verbose_name='Submitted structures'),
        ),
        migrations.AddField(
            model_name='attachmentconstraint',
            name='data_structures',
            field=models.ManyToManyField(through='registry.VersionDetail', to='datastructure.DataStructure', verbose_name='Data structures'),
        ),
        migrations.AddField(
            model_name='attachmentconstraint',
            name='submitted_structure',
            field=models.ManyToManyField(to='registry.SubmittedStructure', verbose_name='Submitted structures'),
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(blank=True, max_length=31, verbose_name='ID')),
                ('annotation_title', models.CharField(blank=True, max_length=127, verbose_name='title')),
                ('annotation_type', models.CharField(blank=True, max_length=31, verbose_name='type')),
                ('annotation_url', models.URLField(blank=True, verbose_name='URL')),
                ('text', models.TextField(blank=True, verbose_name='Text')),
                ('text_en', models.TextField(blank=True, null=True, verbose_name='Text')),
                ('text_el', models.TextField(blank=True, null=True, verbose_name='Text')),
                ('attachment_constraint', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.AttachmentConstraint', verbose_name='Attachment constraint')),
                ('content_constraint', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.ContentConstraint', verbose_name='Content constraint')),
                ('provision_agreement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registry.ProvisionAgreement', verbose_name='Provision agreement')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='contentconstraint',
            index=models.Index(fields=['agency', 'object_id', 'version'], name='registry_co_agency__45a076_idx'),
        ),
        migrations.AddConstraint(
            model_name='contentconstraint',
            constraint=models.UniqueConstraint(fields=('agency', 'object_id', 'version'), name='registry_contentconstraint_unique_maintainable'),
        ),
        migrations.AddIndex(
            model_name='attachmentconstraint',
            index=models.Index(fields=['agency', 'object_id', 'version'], name='registry_at_agency__dd4c4b_idx'),
        ),
        migrations.AddConstraint(
            model_name='attachmentconstraint',
            constraint=models.UniqueConstraint(fields=('agency', 'object_id', 'version'), name='registry_attachmentconstraint_unique_maintainable'),
        ),
    ]
