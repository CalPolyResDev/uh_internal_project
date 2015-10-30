# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from csv import DictReader, DictWriter
from pathlib import Path

from django.conf import settings
from django.db import migrations
from django.db.migrations.operations.special import RunPython
from django.db.utils import IntegrityError


def create_aps_from_csv(apps, schema_editor):
    ResHallWired = apps.get_model('portmap', 'ResHallWired')
    AccessPoint = apps.get_model('portmap', 'AccessPoint')

    ap_import = DictReader((Path(settings.MEDIA_ROOT) / 'aps.csv').open('r'))
    failed_aps = DictWriter((Path(settings.MEDIA_ROOT) / 'aps_failed.csv').open('w'),
                            ['property_id', 'serial_number', 'mac_address', 'ip_address', 'name', 'type', 'room', 'building', 'community', 'jack', ''])
    failed_aps.writeheader()

    for access_point in ap_import:
        port_query = ResHallWired.objects.filter(room__name=access_point['room'].replace('-', ''), room__building__name=access_point['building'], room__building__community__name=access_point['community'])
        if not port_query.exists():
            print("Could not add: " + str(access_point))
            failed_aps.writerow(access_point)
            continue

        new_ap = AccessPoint()
        new_ap.name = access_point['name']
        new_ap.property_id = access_point['property_id']
        new_ap.serial_number = access_point['serial_number']
        new_ap.mac_address = access_point['mac_address']
        new_ap.port = port_query.first()
        new_ap.ip_address = access_point['ip_address']
        new_ap.type = access_point['type']
        try:
            new_ap.save()
        except IntegrityError:
            print("Integrity error when adding: " + str(access_point))
            failed_aps.writerow(access_point)


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0006_auto_20151028_1148'),
    ]

    operations = [
        RunPython(create_aps_from_csv)
    ]
