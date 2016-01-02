"""
.. module:: resnet_internal.apps.portmap.management.import_access_points
   :synopsis: University Housing Internal Port Map Management Access Point Import

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>

"""
from csv import DictReader, DictWriter

from django.core.management import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError

from ...models import Port, AccessPoint


class Command(BaseCommand):
    help = "Imports APs from aps.csv in media"
    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings

        ap_import = DictReader(settings.IMPORT_DATA_PATH.joinpath('aps.csv').open('r'))
        failed_aps = DictWriter(settings.IMPORT_DATA_PATH.joinpath('aps_failed.csv').open('w'),
                                ['property_id', 'serial_number', 'mac_address', 'ip_address', 'name', 'type', 'room', 'building', 'community', 'jack', 'Status', 'Reason Unable to Fix/Notes'])
        failed_aps.writeheader()

        for access_point in ap_import:
            port_query = Port.objects.filter(room__name=access_point['room'].replace('-', ''), room__building__name=access_point['building'], room__building__community__name=access_point['community'])
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
                with transaction.atomic():
                    new_ap.save()
            except IntegrityError:
                print("Integrity error when adding: " + str(access_point))
                failed_aps.writerow(access_point)
