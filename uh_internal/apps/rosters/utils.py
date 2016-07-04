"""
.. module:: resnet_internal.apps.rosters.utils
   :synopsis: University Housing Internal Roster Generator Utilities.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import re

from django.core.exceptions import ImproperlyConfigured

MIN_ROOM = 'A'
MAX_ROOM = 'R'


def room_list_generator(start, end):
    """ Yields a room floor/number combination based on starting and ending rooms.

    :raises: **ImproperlyConfigured** if the start and end rooms do not match the format '(0-9)(a-rA-R)'.

    """

    room_list = []
    room_format = re.compile("(?P<floor>\d)(?P<room>[a-rA-R])")

    try:
        start_floor, start_room = room_format.match(start).groups()
        end_floor, end_room = room_format.match(end).groups()
    except AttributeError:
        raise ImproperlyConfigured("The start or end rooms do not match the format specified.")

    for floor in range(int(start_floor), int(end_floor) + 1):
        if int(start_floor) == int(end_floor):
            lower_bound = ord(start_room.upper())
            upper_bound = ord(end_room.upper())
        elif floor == int(start_floor):
            lower_bound = ord(start_room.upper())
            upper_bound = ord(MAX_ROOM)
        elif floor == int(end_floor):
            lower_bound = ord(MIN_ROOM)
            upper_bound = ord(end_room.upper())
        else:
            lower_bound = ord(MIN_ROOM)
            upper_bound = ord(MAX_ROOM)

        for room in range(lower_bound, upper_bound + 1):
            room_list.append(str(floor) + chr(room))

    return room_list
