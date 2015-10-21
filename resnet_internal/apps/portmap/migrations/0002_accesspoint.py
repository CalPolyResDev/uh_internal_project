# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import resnet_internal.apps.computers.fields


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessPoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=30, verbose_name='DNS Name')),
                ('property_id', models.CharField(max_length=7, unique=True, verbose_name='Property ID')),
                ('serial_number', models.CharField(max_length=9, unique=True, verbose_name='Serial Number')),
                ('mac_address', resnet_internal.apps.computers.fields.MACAddressField(max_length=17, unique=True, verbose_name='MAC Address')),
                ('ip_address', models.GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')),
                ('type', models.CharField(max_length=3, choices=[('5', '5 Ghz'), ('2.4', '2.4 Ghz'), ('AM', 'Air Monitor')], verbose_name='Type')),
                ('port', models.OneToOneField(to='portmap.ResHallWired', related_name='access_point')),
            ],
        ),
    ]
