# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('type', models.CharField(verbose_name='Type of Part', max_length=25)),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity', default=0)),
                ('ordered', models.PositiveIntegerField(verbose_name='Ordered', default=0)),
            ],
            options={
                'verbose_name': 'Printer Part',
                'managed': False,
                'db_table': 'part',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrinterType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('make', models.CharField(verbose_name='Make', max_length=10)),
                ('model', models.CharField(verbose_name='Model', max_length=10)),
            ],
            options={
                'verbose_name': 'Printer Type',
                'managed': False,
                'db_table': 'printertype',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('ticket_id', models.IntegerField(unique=True)),
                ('date_requested', models.DateTimeField()),
                ('priority', models.CharField(max_length=25)),
                ('requestor', models.CharField(max_length=14)),
                ('address', models.CharField(max_length=50)),
                ('status', models.IntegerField(choices=[(0, 'Open'), (1, 'Acknowledged'), (2, 'In Transit'), (3, 'Delivered')])),
            ],
            options={
                'verbose_name': 'Printer Request',
                'managed': False,
                'db_table': 'request',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Request_Parts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Printer Request Parts',
                'managed': False,
                'db_table': 'request_parts',
                'verbose_name_plural': 'Printer Request Parts Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Request_Toner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Printer Request Toner',
                'managed': False,
                'db_table': 'request_toner',
                'verbose_name_plural': 'Printer Request Toner Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Toner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('color', models.CharField(verbose_name='Color', max_length=10)),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity', default=0)),
                ('ordered', models.PositiveIntegerField(verbose_name='Ordered', default=0)),
            ],
            options={
                'verbose_name': 'Printer Toner Cartridge',
                'managed': False,
                'db_table': 'toner',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InventoryEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('email', models.TextField()),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Printer Inventory Email',
            },
            bases=(models.Model,),
        ),
    ]
