# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0005_computer_date_purchased'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domainname',
            name='sr_number',
            field=models.IntegerField(verbose_name='SR Number', null=True, db_column='ticket_id'),
        ),
        migrations.AlterField(
            model_name='pinhole',
            name='sr_number',
            field=models.IntegerField(verbose_name='SR Number', null=True, db_column='ticket_id'),
        ),
    ]
