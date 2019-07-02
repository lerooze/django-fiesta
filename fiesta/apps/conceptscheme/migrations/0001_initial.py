# Generated by Django 2.2.1 on 2019-05-30 15:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ISOConceptReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept_agency', models.CharField(max_length=63)),
                ('concept_scheme_id', models.CharField(max_length=63)),
                ('concept_id', models.CharField(max_length=63)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConceptScheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(default='1.0', max_length=15, validators=[django.core.validators.RegexValidator(re.compile('[0-9]+(\\.[0-9]+)*'), 'Enter a value of type VersionType that has pattern "([0-9]+(\\.[0-9]+)*)"', 'invalid_pattern')])),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('is_final', models.BooleanField(default=False)),
                ('object_id', models.CharField(max_length=63, validators=[django.core.validators.RegexValidator(re.compile('[A-Za-z][A-Za-z0-9_\\-]*'), 'Enter a value of type NCNameIDType that has pattern "([A-Za-z][A-Za-z0-9_\\-]*)"', 'invalid_pattern')], verbose_name='id')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Organisation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('object_id', models.CharField(max_length=63, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='id')),
                ('core_representation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Representation')),
                ('iso_concept_reference', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='concepts', to='conceptscheme.ISOConceptReference')),
                ('wrapper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='concepts', to='conceptscheme.ConceptScheme')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]