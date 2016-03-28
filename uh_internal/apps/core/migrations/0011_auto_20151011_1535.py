# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20151008_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='navbarlink',
            name='url_name',
            field=models.BooleanField(default=True, verbose_name='Is URL Name?'),
        ),
        migrations.AlterField(
            model_name='navbarlink',
            name='icon',
            field=models.CharField(max_length=100, verbose_name='Icon Static File Location', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='navbarlink',
            name='onclick',
            field=models.CharField(max_length=200, verbose_name='Onclick Handler', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='navbarlink',
            name='parent_group',
            field=models.ForeignKey(verbose_name='Parent Link Group', to='core.NavbarLink', related_name='links', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='navbarlink',
            name='url',
            field=models.URLField(verbose_name='URL', blank=True, null=True),
        ),
    ]
