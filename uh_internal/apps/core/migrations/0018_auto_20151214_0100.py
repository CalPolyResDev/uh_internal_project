# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20151214_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subdepartment',
            name='department',
            field=models.ForeignKey(to='core.Department', related_name='sub_departments', verbose_name='Department', null=True),
        ),
    ]
