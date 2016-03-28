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
            name='Computer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('computer_name', models.CharField(unique=True, max_length=25, verbose_name='Computer Name')),
                ('ip_address', models.GenericIPAddressField(unique=True, verbose_name='IP Address', protocol='IPv4')),
                ('mac_address', resnet_internal.apps.computers.fields.MACAddressField(unique=True, max_length=17, verbose_name='MAC Address')),
                ('model', models.CharField(max_length=25, verbose_name='Model')),
                ('serial_number', models.CharField(unique=True, default=None, max_length=20, null=True, verbose_name='Serial Number', blank=True)),
                ('property_id', models.CharField(unique=True, default=None, max_length=50, null=True, verbose_name='Cal Poly Property ID', blank=True)),
                ('dn', models.CharField(max_length=250, verbose_name='Distinguished Name')),
                ('description', models.CharField(max_length=100, verbose_name='Description')),
                ('department', models.ForeignKey(verbose_name='Department', to='core.Department')),
                ('sub_department', models.ForeignKey(verbose_name='Sub Department', to='core.SubDepartment')),
            ],
            options={
                'verbose_name': 'University Housing Computer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DomainName',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Address', protocol='IPv4')),
                ('domain_name', models.CharField(max_length=100, verbose_name='Domain Name')),
                ('sr_number', models.IntegerField(max_length=11, null=True, verbose_name='SR Number', db_column='ticket_id')),
            ],
            options={
                'verbose_name': 'University Housing Domain Name',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pinhole',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Address', protocol='IPv4')),
                ('service_name', models.CharField(max_length=50, verbose_name='Service Name')),
                ('inner_fw', models.BooleanField(default=None, verbose_name='Inner Firewall')),
                ('border_fw', models.BooleanField(default=None, verbose_name='Border Firewall')),
                ('tcp_ports', resnet_internal.apps.computers.fields.ListField(verbose_name='TCP Ports')),
                ('udp_ports', resnet_internal.apps.computers.fields.ListField(verbose_name='TCP Ports')),
                ('sr_number', models.IntegerField(max_length=11, null=True, verbose_name='SR Number', db_column='ticket_id')),
            ],
            options={
                'verbose_name': 'University Housing Pinhole',
            },
            bases=(models.Model,),
        ),
    ]
