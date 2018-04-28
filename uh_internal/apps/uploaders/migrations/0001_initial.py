# Generated by Django 2.0.4 on 2018-04-27 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Uploaders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True, verbose_name='Uploader Name')),
                ('last_run', models.DateTimeField(verbose_name='Last DateTime run')),
                ('successful', models.BooleanField(verbose_name='If the run was successful')),
            ],
            options={
                'verbose_name': 'Uploader',
                'verbose_name_plural': 'Uploaders',
            },
        ),
    ]