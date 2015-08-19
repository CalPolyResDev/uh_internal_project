# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150708_1743'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkDevice',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('display_name', models.CharField(verbose_name='Display Name', max_length=100)),
                ('dns_name', models.CharField(verbose_name='DNS Name', max_length=75)),
                ('ip_address', models.IPAddressField(verbose_name='IP Address')),
            ],
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='ip_address',
            field=models.GenericIPAddressField(verbose_name='IP Address', protocol='IPv4'),
        ),
    ]
