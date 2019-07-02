# Generated by Django 2.2.1 on 2019-05-30 15:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Codelist',
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
                'ordering': ['object_id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('object_id', models.CharField(blank=True, max_length=63, validators=[django.core.validators.RegexValidator(re.compile('^[A-Za-z0-9_@$\\-]+$'), 'Enter a value of type IDType that has pattern "(^[A-Za-z0-9_@$\\-]+$)"', 'invalid_pattern')], verbose_name='ID')),
                ('wrapper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelist.Codelist', verbose_name='Codelist')),
            ],
            options={
                'ordering': ['object_id'],
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='codelist',
            index=models.Index(fields=['object_id'], name='codelist_co_object__3ebb31_idx'),
        ),
        migrations.AddIndex(
            model_name='codelist',
            index=models.Index(fields=['agency'], name='codelist_co_agency__b97d68_idx'),
        ),
        migrations.AddIndex(
            model_name='codelist',
            index=models.Index(fields=['object_id', 'version'], name='codelist_co_object__7d5c89_idx'),
        ),
        migrations.AddIndex(
            model_name='codelist',
            index=models.Index(fields=['object_id', 'agency', 'version'], name='codelist_co_object__238bd1_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='codelist',
            unique_together={('object_id', 'agency', 'version')},
        ),
        migrations.AddIndex(
            model_name='code',
            index=models.Index(fields=['object_id'], name='codelist_co_object__ae00fa_idx'),
        ),
        migrations.AddIndex(
            model_name='code',
            index=models.Index(fields=['wrapper'], name='codelist_co_wrapper_b4221a_idx'),
        ),
        migrations.AddIndex(
            model_name='code',
            index=models.Index(fields=['wrapper', 'object_id'], name='codelist_co_wrapper_ef1ff4_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='code',
            unique_together={('wrapper', 'object_id')},
        ),
    ]
