# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_building_community'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='resnetinternaluser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='resnetinternaluser',
            name='email',
            field=models.EmailField(blank=True, verbose_name='Email Address', max_length=254),
        ),
        migrations.AlterField(
            model_name='resnetinternaluser',
            name='groups',
            field=models.ManyToManyField(verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', blank=True, related_name='user_set', to='auth.Group', related_query_name='user'),
        ),
        migrations.AlterField(
            model_name='resnetinternaluser',
            name='last_login',
            field=models.DateTimeField(blank=True, verbose_name='last login', null=True),
        ),
    ]
