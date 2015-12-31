"""
.. module:: resnet_internal.apps.portmap.management.import_ports
   :synopsis: University Housing Internal Port Map Management Port Import

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>

"""
from csv import DictReader, DictWriter

from django.core.management import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Imports Ports from ports.csv in media"
    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings
        from ....core.models import Room
        from ...models import Port

        port_import = DictReader(settings.IMPORT_DATA_PATH.joinpath('ports.csv').open('r'))

        failed_ports = DictWriter(settings.IMPORT_DATA_PATH.joinpath('ports_failed.csv').open('w'),
                                ['community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'notes'])
        failed_ports.writeheader()

        for port in port_import:
            room_query = Room.objects.filter(building__name=port['building'],
                                             building__community__name=port['community'],
                                             name=port['room'])

            if not room_query.exists():
                print("Could not add: " + str(port))
                failed_ports.writerow(port)
                continue

            port_query = Port.objects.filter(
                port=port['port'],
                blade=port['blade'],
                jack=port['jack'],
                switch_name=port['switch_name'],
                switch_ip=port['switch_ip'],
                room=room_query.first(),
            )

            if not port_query.exists():
                new_port = Port()
                new_port.room = room_query.first()
                new_port.switch_ip = port['switch_ip']
                new_port.switch_name = port['switch_name']
                new_port.jack = port['jack']
                new_port.blade = int(port['blade'])
                new_port.port = int(port['port'])

                try:
                    with transaction.atomic():
                        new_port.save()
                except IntegrityError:
                    print("Integrity error when adding: " + str(port))
                    failed_ports.writerow(port)
