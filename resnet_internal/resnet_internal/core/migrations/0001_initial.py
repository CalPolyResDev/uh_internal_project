# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResNetInternalUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(unique=True, max_length=30, verbose_name='Username')),
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
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'ResNet Internal User',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DailyDuties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=15, verbose_name=b'Duty Name')),
                ('last_checked', models.DateTimeField(verbose_name=b'Last DateTime Checked')),
                ('last_user', models.ForeignKey(verbose_name=b'Last User to Check', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteAnnouncements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name=b'Title')),
                ('description', models.TextField(verbose_name=b'Description')),
                ('created', models.DateTimeField(verbose_name=b'Entry Creation Date')),
            ],
            options={
                'get_latest_by': 'created',
                'verbose_name': 'Site Announcement',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StaffMapping',
            fields=[
            ],
            options={
                'verbose_name': 'Campus Staff Mapping',
                'db_table': 'staffmapping',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
