# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150107_0948'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Department Name')),
            ],
            options={
                'verbose_name': 'UH Department',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubDepartment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Sub Department Name')),
            ],
            options={
                'verbose_name': 'UH Sub Department',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='department',
            name='sub_departments',
            field=models.ManyToManyField(to='core.SubDepartment'),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='building',
            options={'managed': False, 'verbose_name': 'UH Building'},
        ),
        migrations.AlterModelOptions(
            name='community',
            options={'managed': False, 'verbose_name': 'UH Community', 'verbose_name_plural': 'UH Communities'},
        ),
    ]
