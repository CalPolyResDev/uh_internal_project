# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 20:55
from __future__ import unicode_literals

from django.db import migrations, models
import uh_internal.apps.computers.fields


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_auto_20160405_1354'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clearpassloginattempt',
            options={'verbose_name': 'ClearPass Login Attempt'},
        ),
        migrations.AlterField(
            model_name='clearpassloginattempt',
            name='client_mac_address',
            field=uh_internal.apps.computers.fields.MACAddressField(db_index=True, max_length=17),
        ),
        migrations.AlterField(
            model_name='clearpassloginattempt',
            name='username',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True),
        ),
    ]