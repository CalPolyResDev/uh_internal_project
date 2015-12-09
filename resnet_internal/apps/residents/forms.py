"""
.. module:: reslife_internal.apps.residents.forms
   :synopsis: ResLife Internal Resident Lookup Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, CharField, ChoiceField

from rmsconnector.constants import COMMUNITIES, ALL_BUILDINGS


class FullNameSearchForm(Form):
    first_name = CharField(label='First Name', error_messages={'required': 'A first name is required'})
    last_name = CharField(label='Last Name', error_messages={'required': 'A last name is required'})


class PrincipalNameSearchForm(Form):
    principal_name = CharField(label='Email Address', max_length=20, error_messages={'required': 'A cal poly email address is required'})


class AddressSearchForm(Form):
    community = ChoiceField(label='Community', error_messages={'required': 'A community is required'})
    building = ChoiceField(label='Building', error_messages={'required': 'A building is required'})
    room = CharField(label='Room', error_messages={'required': 'A room number is required'})

    def __init__(self, *args, **kwargs):
        super(AddressSearchForm, self).__init__(*args, **kwargs)

        self.fields["community"].choices.append(("", "---------"))
        self.fields["community"].choices.extend([(community, community) for community in COMMUNITIES])
        self.fields["building"].choices.extend([(building, building) for building in ALL_BUILDINGS])
