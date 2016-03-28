# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150819_1002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='buildings',
        ),
        migrations.AddField(
            model_name='building',
            name='community',
            field=models.ForeignKey(related_name='buildings', to='core.Community', default=1, verbose_name='Community'),
            preserve_default=False,
        ),
    ]
