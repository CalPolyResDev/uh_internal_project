# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import resnet_internal.apps.computers.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('printer_name', models.CharField(max_length=60, verbose_name='Printer Name', unique=True)),
                ('ip_address', models.GenericIPAddressField(protocol='IPv4', verbose_name='IP Address', unique=True)),
                ('mac_address', resnet_internal.apps.computers.fields.MACAddressField(max_length=17, verbose_name='MAC Address', unique=True)),
                ('model', models.CharField(max_length=25, verbose_name='Model')),
                ('serial_number', models.CharField(max_length=20, blank=True, null=True, default=None, verbose_name='Serial Number', unique=True)),
                ('property_id', models.CharField(max_length=50, blank=True, null=True, default=None, verbose_name='Cal Poly Property ID', unique=True)),
                ('description', models.CharField(max_length=100, verbose_name='Description')),
                ('department', models.ForeignKey(verbose_name='Department', to='core.Department')),
                ('sub_department', models.ForeignKey(verbose_name='Sub Department', to='core.SubDepartment')),
            ],
            options={
                'verbose_name': 'University Housing Printer',
            },
            bases=(models.Model,),
        ),
    ]
