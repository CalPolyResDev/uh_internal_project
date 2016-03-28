# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import resnet_internal.apps.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20151008_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='ADGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distinguished_name', models.CharField(max_length=250, unique=True, verbose_name='Distinguished Name')),
                ('common_name', models.CharField(max_length=50, verbose_name='Common Name')),
            ],
        ),
        migrations.CreateModel(
            name='NavbarLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=50, verbose_name='Display Name')),
                ('icon', models.CharField(max_length=100, verbose_name='Icon Static File Location')),
                ('sequence_index', models.SmallIntegerField(verbose_name='Sequence Index')),
                ('url', models.URLField(null=True, verbose_name='URL')),
                ('groups', models.ManyToManyField(verbose_name='AD Groups', to='core.ADGroup')),
                ('parent_group', models.ForeignKey(related_name='links', null=True, to='core.NavbarLink', verbose_name='Parent Link Group')),
            ],
        ),
        migrations.AlterModelManagers(
            name='resnetinternaluser',
            managers=[
                ('objects', resnet_internal.apps.core.models.InternalUserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='resnetinternaluser',
            name='open_links_in_frame',
        ),
        migrations.AddField(
            model_name='resnetinternaluser',
            name='ad_groups',
            field=models.ManyToManyField(to='core.ADGroup'),
        ),
    ]
