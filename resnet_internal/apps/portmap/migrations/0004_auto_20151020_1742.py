# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.migrations.operations.special import RunPython


def create_rooms_from_portmap(apps, schema_editor):
    ResHallWired = apps.get_model('portmap', 'ResHallWired')
    Room = apps.get_model('core', 'Room')
    Building = apps.get_model('core', 'Building')
    Community = apps.get_model('core', 'Community')

    for port in ResHallWired.objects.all():
        q = Room.objects.filter(building__community=port.building.community, building=port.building, name=port.room)
        if q.exists():
            port.room_new = q.first()
        else:
            # Fix Port Building assignments
            if port.building.community.id != port.community.id:
                building_query = Building.objects.filter(community=port.community, name=port.building.name)
                if building_query.exists():
                    port.building = building_query.first()
                else:
                    port.community = Community.objects.get(id=port.building.community.id)
                port.save()

            new_room = Room(name=port.room, building=port.building)
            new_room.save()
            port.room_new = new_room
        port.save()


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0003_reshallwired_room_new'),
    ]

    operations = [
        RunPython(create_rooms_from_portmap)
    ]
