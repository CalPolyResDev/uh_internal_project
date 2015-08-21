# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150814_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkdevice',
            name='ip_address',
            field=models.GenericIPAddressField(verbose_name='IP Address', protocol='IPv4'),
        ),
    ]
