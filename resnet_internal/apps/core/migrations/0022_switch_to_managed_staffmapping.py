# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-25 23:51
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.migrations.operations.special import RunPython


def populate_staff_mapping(apps, schema_editor):
    StaffMapping = apps.get_model('core', 'StaffMapping')

    StaffMapping.objects.create(
        title="ITS: SRS Account Manager",
        name="Anita West",
        email="awest@calpoly.edu",
        extension=2516
    )
    StaffMapping.objects.create(
        title="Housing: Information Technology Consultant",
        name="Julie Gibson",
        email="jagibson@calpoly.edu",
        extension=7159
    )
    StaffMapping.objects.create(
        title="ResNet: Assistant Resident Coordinator",
        name="Jeffrey F. Porter",
        email="jfporter@calpoly.edu",
        extension=5619
    )
    StaffMapping.objects.create(
        title="ResNet: Resident Coordinator",
        name="Jeannie Abney",
        email="jabney@calpoly.edu",
        extension=5602
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_housing_user_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=35, verbose_name='Title', unique=True)),
                ('name', models.CharField(max_length=50, verbose_name='Full Name')),
                ('email', models.CharField(max_length=8, verbose_name='Email Address')),
                ('extension', models.PositiveSmallIntegerField(verbose_name='Telephone Extension')),
            ],
            options={
                'verbose_name': 'Campus Staff Mapping',
            },
            bases=(models.Model,),
        ),
        RunPython(populate_staff_mapping),
    ]
