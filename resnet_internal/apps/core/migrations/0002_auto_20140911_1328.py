# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'Building Name')),
                ('rms_id', models.IntegerField(verbose_name=b'RMS Building ID')),
            ],
            options={
                'verbose_name': 'Building',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'Community Name')),
                ('rms_id', models.IntegerField(verbose_name=b'RMS Community ID')),
            ],
            options={
                'verbose_name': 'Community',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='building',
            name='community',
            field=models.ForeignKey(verbose_name=b'Community', to='core.Community'),
            preserve_default=True,
        ),
    ]
