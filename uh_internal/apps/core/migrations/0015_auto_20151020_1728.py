# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20151014_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Room Numbers', max_length=10)),
                ('building', models.ForeignKey(verbose_name='Building', to='core.Building', related_name='rooms')),
            ],
        ),
        migrations.AlterField(
            model_name='adgroup',
            name='display_name',
            field=models.CharField(verbose_name='Display Name', max_length=50),
        ),
    ]
