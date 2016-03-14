# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-12 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('printerrequests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=25, verbose_name='Type of Part')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('ordered', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Printer Part',
            },
        ),
        migrations.CreateModel(
            name='PrinterType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(max_length=10)),
                ('model', models.CharField(max_length=10)),
                ('servicable', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Printer Type',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.IntegerField(unique=True)),
                ('date_requested', models.DateTimeField()),
                ('priority', models.CharField(max_length=25)),
                ('requestor', models.CharField(max_length=14)),
                ('address', models.CharField(max_length=50)),
                ('status', models.IntegerField(choices=[(0, 'Open'), (1, 'Acknowledged'), (2, 'In Transit'), (3, 'Delivered')])),
                ('parts', models.ManyToManyField(to='printerrequests.Part')),
            ],
            options={
                'verbose_name': 'Printer Request',
            },
        ),
        migrations.CreateModel(
            name='Toner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=10)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('ordered', models.PositiveIntegerField(default=0)),
                ('printer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='printerrequests.PrinterType', verbose_name='Associated Printer')),
            ],
            options={
                'verbose_name': 'Printer Toner Cartridge',
            },
        ),
        migrations.AddField(
            model_name='request',
            name='toner',
            field=models.ManyToManyField(to='printerrequests.Toner'),
        ),
        migrations.AlterUniqueTogether(
            name='printertype',
            unique_together=set([('make', 'model')]),
        ),
        migrations.AddField(
            model_name='part',
            name='printer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='printerrequests.PrinterType', verbose_name='Associated Printer'),
        ),
        migrations.AlterUniqueTogether(
            name='toner',
            unique_together=set([('color', 'printer')]),
        ),
        migrations.AlterUniqueTogether(
            name='part',
            unique_together=set([('type', 'printer')]),
        ),
    ]