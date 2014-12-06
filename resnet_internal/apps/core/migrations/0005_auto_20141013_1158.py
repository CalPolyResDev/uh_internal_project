# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20140911_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechFlair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flair', models.CharField(unique=True, verbose_name='Flair', max_length=30)),
                ('tech', models.ForeignKey(verbose_name='Technician', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='dailyduties',
            name='last_checked',
            field=models.DateTimeField(verbose_name='Last DateTime Checked'),
        ),
        migrations.AlterField(
            model_name='dailyduties',
            name='last_user',
            field=models.ForeignKey(verbose_name='Last User to Check', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dailyduties',
            name='name',
            field=models.CharField(unique=True, verbose_name='Duty Name', max_length=15),
        ),
        migrations.AlterField(
            model_name='siteannouncements',
            name='created',
            field=models.DateTimeField(verbose_name='Entry Creation Date'),
        ),
        migrations.AlterField(
            model_name='siteannouncements',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='siteannouncements',
            name='title',
            field=models.CharField(verbose_name='Title', max_length=150),
        ),
    ]
