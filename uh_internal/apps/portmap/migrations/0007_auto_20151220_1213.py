# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0006_auto_20151028_1148'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ResHallWired',
            new_name='Port',
        ),
        migrations.AlterModelOptions(
            name='port',
            options={},
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='port',
            field=models.OneToOneField(related_name='access_point', to='portmap.Port'),
        ),
    ]
