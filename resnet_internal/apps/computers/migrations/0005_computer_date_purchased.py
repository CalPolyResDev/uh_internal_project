# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0004_auto_20150324_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='computer',
            name='date_purchased',
            field=models.DateField(default=datetime.date(2015, 3, 24), verbose_name='Date Purchased'),
            preserve_default=False,
        ),
    ]
