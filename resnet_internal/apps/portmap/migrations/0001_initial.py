# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_building_community'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResHallWired',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('room', models.CharField(verbose_name='Room', max_length=10)),
                ('switch_ip', models.GenericIPAddressField(protocol='IPv4', verbose_name='Switch IP')),
                ('switch_name', models.CharField(verbose_name='Switch Name', max_length=35)),
                ('jack', models.CharField(verbose_name='Jack', max_length=5)),
                ('blade', models.PositiveSmallIntegerField(verbose_name='Blade')),
                ('port', models.PositiveSmallIntegerField(verbose_name='Port')),
                ('vlan', models.CharField(verbose_name='vLan', max_length=7)),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('building', models.ForeignKey(verbose_name='Building', to='core.Building')),
                ('community', models.ForeignKey(verbose_name='Community', to='core.Community')),
            ],
            options={
                'verbose_name': 'Residence Halls Wired Port',
            },
            bases=(models.Model,),
        ),
    ]
