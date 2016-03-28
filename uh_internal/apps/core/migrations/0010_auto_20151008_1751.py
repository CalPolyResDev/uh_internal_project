# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20151008_1520'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adgroup',
            options={'verbose_name': 'AD Group'},
        ),
        migrations.AddField(
            model_name='navbarlink',
            name='onclick',
            field=models.CharField(verbose_name='Onclick Handler', null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='navbarlink',
            name='open_in_new',
            field=models.BooleanField(default=False, verbose_name='Open in New Window'),
        ),
    ]
