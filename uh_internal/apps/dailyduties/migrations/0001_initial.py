# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyDuties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=15, unique=True, verbose_name='Duty Name')),
                ('last_checked', models.DateTimeField(verbose_name='Last DateTime Checked')),
                ('last_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Last User to Check')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
