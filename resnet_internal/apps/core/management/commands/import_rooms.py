"""
.. module:: resnet_internal.apps.portmap.management.import_rooms
   :synopsis: ResNet Internal Residence Halls Port Map Management Room Import

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>
"""
from csv import DictReader, DictWriter
from pathlib import Path

from django.core.management import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError

from ...models import Room


class Command(BaseCommand):
    help = "Imports Rooms from rooms.csv in media"
    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings

        room_import = DictReader((Path(settings.MEDIA_ROOT) / 'rooms.csv').open('r'))
        failed_rooms = DictWriter((Path(settings.MEDIA_ROOT) / 'rooms_failed.csv').open('w'), ['community', 'building', 'room'])
        failed_rooms.writeheader()

        for room in room_import:
            building_query = Room.objects.filter(building__name=room['building'], building__community__name=room['community'])

            if not building_query.exists():
                print("Could not add: " + str(room))
                failed_rooms.writerow(room)
                continue

            new_room = Room()
            new_room.name = room['name']
            new_room.building = building_query.first()

            try:
                with transaction.atomic():
                    new_room.save()
            except IntegrityError:
                print("Integrity error when adding: " + str(room))
                failed_rooms.writerow(room)
