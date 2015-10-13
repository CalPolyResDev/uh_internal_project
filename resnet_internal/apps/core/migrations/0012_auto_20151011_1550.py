# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20151011_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navbarlink',
            name='url_name',
            field=models.CharField(null=True, blank=True, max_length=100),
        ),
    ]
