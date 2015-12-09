"""
.. module:: reslife_internal.apps.residents.forms
   :synopsis: ResLife Internal Resident Lookup Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.forms import ChainedModelChoiceField, ChainedChoicesForm
from django.core.urlresolvers import reverse_lazy
from django.forms import Form, CharField, ModelChoiceField

from ..core.models import Building, Community


class FullNameSearchForm(Form):
    first_name = CharField(label='First Name', error_messages={'required': 'A first name is required'})
    last_name = CharField(label='Last Name', error_messages={'required': 'A last name is required'})


class PrincipalNameSearchForm(Form):
    principal_name = CharField(label='Email Address', max_length=20, error_messages={'required': 'A cal poly email address is required'})


class AddressSearchForm(ChainedChoicesForm):
    community = ModelChoiceField(queryset=Community.objects.all(), label='Community', error_messages={'required': 'A community is required'})
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building, label='Building', error_messages={'required': 'A building is required'})
    room = CharField(label='Room', error_messages={'required': 'A room number is required'})
