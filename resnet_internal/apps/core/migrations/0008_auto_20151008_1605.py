# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    ResNetInternalUser = apps.get_model('core', 'ResNetInternalUser')
    db_alias = schema_editor.connection.alias
    for user in ResNetInternalUser.objects.using(db_alias).all():
        if not user.username.endswith('@calpoly.edu'):
            user.username = user.username + '@calpoly.edu'
            user.save()


def reverse_func(apps, schema_editor):
    ResNetInternalUser = apps.get_model('core', 'ResNetInternalUser')
    db_alias = schema_editor.connection.alias
    for user in ResNetInternalUser.objects.using(db_alias).all():
        if user.username.endswith('@calpoly.edu'):
            user.username = user.username[0:user.username.find('@calpoly.edu')]
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150901_1401'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
