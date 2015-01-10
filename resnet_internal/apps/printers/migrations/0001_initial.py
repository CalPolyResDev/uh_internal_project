# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import resnet_internal.apps.computers.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150109_1149'),
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('printer_name', models.CharField(max_length=60, unique=True, verbose_name='Printer Name')),
                ('ip_address', models.GenericIPAddressField(unique=True, verbose_name='IP Address', protocol='IPv4')),
                ('mac_address', resnet_internal.apps.computers.fields.MACAddressField(max_length=17, unique=True, verbose_name='MAC Address')),
                ('model', models.CharField(max_length=25, verbose_name='Model')),
                ('serial_number', models.CharField(max_length=20, unique=True, null=True, verbose_name='Serial Number', blank=True, default=None)),
                ('property_id', models.CharField(max_length=50, unique=True, null=True, verbose_name='Cal Poly Property ID', blank=True, default=None)),
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
