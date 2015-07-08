# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='Building Name', max_length=30)),
            ],
            options={
                'verbose_name': 'University Housing Building',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='Community Name', max_length=30)),
                ('buildings', models.ManyToManyField(to='core.Building')),
            ],
            options={
                'verbose_name': 'University Housing Community',
                'verbose_name_plural': 'University Housing Communities',
            },
            bases=(models.Model,),
        ),
    ]
