# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.migrations.operations.special import RunPython


def populate_ap_type(apps, schema_editor):
    AccessPoint = apps.get_model('portmap', 'AccessPoint')

    type_choices = ['5', '2.4', 'AM']
    type_map = {type_choices[index]: index for index in range(len(type_choices))}

    for accesspoint in AccessPoint.objects.all():
        accesspoint.ap_type = type_map[accesspoint.type]
        accesspoint.save()


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0008_remove_port_vlan'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesspoint',
            name='ap_type',
            field=models.PositiveSmallIntegerField(verbose_name='Type', default=0, choices=[(0, '5 Ghz'), (1, '2.4 Ghz'), (2, 'Air Monitor')]),
            preserve_default=False,
        ),
        RunPython(populate_ap_type),
    ]
