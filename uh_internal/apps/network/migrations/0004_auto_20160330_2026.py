# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-30 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_clearpassloginattempt_alerts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clearpassloginattempt',
            name='accepted',
        ),
        migrations.AddField(
            model_name='clearpassloginattempt',
            name='result',
            field=models.PositiveSmallIntegerField(choices=[(0, 'ACCEPT'), (1, 'REJECT'), (2, 'TIMEOUT')], default=0),
            preserve_default=False,
        ),
    ]