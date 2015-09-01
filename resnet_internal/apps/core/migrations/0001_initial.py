# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('staff_title', models.CharField(max_length=35, verbose_name='Staff Title', unique=True)),
                ('staff_name', models.CharField(max_length=50, verbose_name='Staff Full Name')),
                ('staff_alias', models.CharField(max_length=8, verbose_name='Staff Alias')),
                ('staff_ext', models.IntegerField(max_length=4, verbose_name='Staff Telephone Extension')),
            ],
            options={
                'verbose_name': 'Campus Staff Mapping',
                'db_table': 'staffmapping',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResNetInternalUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('username', models.CharField(max_length=30, verbose_name='Username', unique=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='Last Name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='Email Address', blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_new_tech', models.NullBooleanField()),
                ('is_net_admin', models.BooleanField(default=False)),
                ('is_telecom', models.BooleanField(default=False)),
                ('is_tag', models.BooleanField(default=False)),
                ('is_tag_readonly', models.BooleanField(default=False)),
                ('is_technician', models.BooleanField(default=False)),
                ('is_rn_staff', models.BooleanField(default=False)),
                ('is_developer', models.BooleanField(default=False)),
                ('onity_complete', models.BooleanField(default=False)),
                ('srs_complete', models.BooleanField(default=False)),
                ('payroll_complete', models.BooleanField(default=False)),
                ('orientation_complete', models.BooleanField(default=False)),
                ('open_links_in_frame', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', verbose_name='groups', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='user permissions', related_name='user_set', help_text='Specific permissions for this user.', related_query_name='user')),
            ],
            options={
                'verbose_name': 'ResNet Internal User',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50, verbose_name='Department Name')),
            ],
            options={
                'verbose_name': 'University Housing Department',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteAnnouncements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('created', models.DateTimeField(verbose_name='Entry Creation Date')),
            ],
            options={
                'verbose_name': 'Site Announcement',
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubDepartment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50, verbose_name='Sub Department Name')),
            ],
            options={
                'verbose_name': 'University Housing Sub Department',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TechFlair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('flair', models.CharField(max_length=30, verbose_name='Flair', unique=True)),
                ('tech', models.ForeignKey(verbose_name='Technician', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tech Flair',
                'verbose_name_plural': 'Tech Flair',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='department',
            name='sub_departments',
            field=models.ManyToManyField(to='core.SubDepartment'),
            preserve_default=True,
        ),
    ]
