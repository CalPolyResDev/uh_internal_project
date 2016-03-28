# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
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
