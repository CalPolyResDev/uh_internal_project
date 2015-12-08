"""
.. module:: reslife_internal.apps.rosters.forms
   :synopsis: ResLife Internal Roster Generator Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import re

from clever_selects.form_fields import ChainedModelChoiceField
from django.forms import Form, CharField, ChoiceField, ValidationError, ModelChoiceField
from django.core.urlresolvers import reverse_lazy

from rmsconnector.constants import CSD_DOMAINS, SIERRA_MADRE, YOSEMITE

from ..core.models import Building, Community


class GenerationForm(Form):
    hall = ChoiceField(label='Hall', error_messages={'required': 'A hall is required'})

    def __init__(self, *args, **kwargs):
        super(GenerationForm, self).__init__(*args, **kwargs)

        self.fields["hall"].choices.append(("", "-------------"))
        self.fields["hall"].choices = [(hall, hall) for hall in CSD_DOMAINS]


class AddressRangeSearchForm(Form):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building, label="Building", error_messages={'required': 'A building is required'})
    start_room = CharField(label='Start Room', error_messages={'required': 'A starting room number is required'})
    end_room = CharField(label='End Room', error_messages={'required': 'An ending room number is required'})

    def __init__(self, *args, **kwargs):
        super(AddressRangeSearchForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AddressRangeSearchForm, self).clean()

        community = cleaned_data.get("community")
        start = cleaned_data.get("start_room")
        end = cleaned_data.get("end_room")

        if start and end:
            # Check the room format for certain buildings
            if community == SIERRA_MADRE or community == YOSEMITE:
                room_format = re.compile("(?P<floor>\d)(?P<room>[a-rA-R])")

                try:
                    start_floor, start_room = room_format.match(start).groups()
                except AttributeError:
                    raise ValidationError("The format of start room is incorrect for community %s. Use '(0-9)(A-R)'" % community)

                try:
                    end_floor, end_room = room_format.match(end).groups()
                except AttributeError:
                    raise ValidationError("The format of end room is incorrect for building %s. Use '(0-9)(A-R)'" % community)

                # Check to make sure start_floor is less than end_floor
                if int(end_floor) < int(start_floor):
                    raise ValidationError("The starting room must come before the ending room.")

            else:
                # Make sure the start comes before the end
                start = int(''.join([x for x in start if x.isdigit()]))
                end = int(''.join([x for x in end if x.isdigit()]))

                if end < start:
                    raise ValidationError("The starting room must come before the ending room.")

        return cleaned_data
