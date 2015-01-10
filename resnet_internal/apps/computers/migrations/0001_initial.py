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
            name='Computer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('computer_name', models.CharField(max_length=25, verbose_name='Computer Name', unique=True)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Address', unique=True, protocol='IPv4')),
                ('mac_address', resnet_internal.apps.computers.fields.MACAddressField(max_length=17, verbose_name='MAC Address', unique=True)),
                ('model', models.CharField(max_length=25, verbose_name='Model')),
                ('serial_number', models.CharField(max_length=20, verbose_name='Serial Number', unique=True, null=True)),
                ('property_id', models.CharField(max_length=50, verbose_name='Cal Poly Property ID', unique=True, null=True)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Address', protocol='IPv4')),
                ('domain_name', models.CharField(max_length=100, verbose_name='Domain Name')),
                ('sr_number', models.IntegerField(db_column='ticket_id', max_length=11, verbose_name='SR Number', null=True)),
            ],
            options={
                'verbose_name': 'University Housing Domain Name',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pinhole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Address', protocol='IPv4')),
                ('service_name', models.CharField(max_length=50, verbose_name='Service Name')),
                ('inner_fw', models.BooleanField(default=None, verbose_name='Inner Firewall')),
                ('border_fw', models.BooleanField(default=None, verbose_name='Border Firewall')),
                ('tcp_ports', resnet_internal.apps.computers.fields.ListField(verbose_name='TCP Ports')),
                ('udp_ports', resnet_internal.apps.computers.fields.ListField(verbose_name='TCP Ports')),
                ('sr_number', models.IntegerField(db_column='ticket_id', max_length=11, verbose_name='SR Number', null=True)),
            ],
            options={
                'verbose_name': 'University Housing Pinhole',
            },
            bases=(models.Model,),
        ),
    ]
