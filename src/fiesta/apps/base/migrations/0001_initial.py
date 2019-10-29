# Generated by Django 3.0b1 on 2019-10-29 18:12

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import re
import versionfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(blank=True, db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('[A-Za-z][A-Za-z0-9_\\-]*(\\.[A-Za-z][A-Za-z0-9_\\-]*)*'), 'Enter a value of type NestedNCNameIDType that has pattern "([A-Za-z][A-Za-z0-9_\\-]*(\\.[A-Za-z][A-Za-z0-9_\\-]*)*)"', 'invalid_pattern')], verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Agency',
                'verbose_name_plural': 'Agencies',
                'abstract': False,
            },
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
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataConsumer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('object_id', models.CharField(db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Data consumer',
                'verbose_name_plural': 'Data consumers',
                'ordering': ['container', 'object_id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataConsumerScheme',
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
            ],
            options={
                'verbose_name': 'Data consumer scheme',
                'verbose_name_plural': 'Data consumer schemes',
                'ordering': ['agency', 'object_id', '-version'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('object_id', models.CharField(db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Data provider',
                'verbose_name_plural': 'Data providers',
                'ordering': ['container', 'object_id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataProviderScheme',
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
            ],
            options={
                'verbose_name': 'Data provider scheme',
                'verbose_name_plural': 'Data provider schemes',
                'ordering': ['agency', 'object_id', '-version'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganisationUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('name_el', models.CharField(blank=True, max_length=127, null=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=511, verbose_name='Description')),
                ('description_en', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('description_el', models.CharField(blank=True, max_length=511, null=True, verbose_name='Description')),
                ('object_id', models.CharField(db_index=True, max_length=31, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Organisation unit',
                'verbose_name_plural': 'Organisation units',
                'ordering': ['container', 'object_id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganisationUnitScheme',
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
                'verbose_name': 'Organisation unit scheme',
                'verbose_name_plural': 'Organisation unit schemes',
                'ordering': ['agency', 'object_id', '-version'],
                'abstract': False,
            },
        ),
    ]
