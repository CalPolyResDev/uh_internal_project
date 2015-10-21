"""
.. module:: resnet_internal.apps.accesspoints.autocomplete_light_registry
   :synopsis: ResNet Internal Access Points Index AutoComplete Registry.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>

"""

from autocomplete_light import AutocompleteModelBase

import autocomplete_light.shortcuts as al

from ..core.models import Community, Building, Room
from .models import ResHallWired, AccessPoint


al.register(Community, search_fields=['name'], autocomplete_js_attributes={'placeholder': 'Community name...'})


class BuildingAutocomplete(AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Building name...'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        community_id = self.request.GET.get('community_id', None)

        choices = self.choices.all()
        if q:
            choices = choices.filter(name__contains=q)
        if community_id:
            choices = choices.filter(community__id=community_id)

        return self.order_choices(choices)[0:self.limit_choices]

al.register(Building, BuildingAutocomplete)


class RoomAutocomplete(AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Room name...'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        building_id = self.request.GET.get('building_id', None)

        choices = self.choices.all()
        if q:
            choices = choices.filter(name__contains=q)
        if building_id:
            choices = choices.filter(building__id=building_id)

        return self.order_choices(choices)[0:self.limit_choices]

al.register(Room, RoomAutocomplete)


class ResHallWiredAutocomplete(AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'Port Name...'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        room_id = self.request.GET.get('room_id', None)

        choices = self.choices.all()
        if q:
            choices = choices.filter(jack__contains=q)
        if room_id:
            choices = choices.filter(room__id=room_id)

        return self.order_choices(choices)[0:self.limit_choices]

al.register(ResHallWired, ResHallWiredAutocomplete)
