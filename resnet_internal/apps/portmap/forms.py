"""
.. module:: resnet_internal.apps.portmap.forms
   :synopsis: ResNet Internal Portmap Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from autocomplete_light import ModelForm as ACModelForm, ModelChoiceField as ACModelChoiceField
from django.forms import ModelForm

from .models import ResHallWired, AccessPoint


class ResHallWiredPortCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ResHallWiredPortCreateForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = ResHallWired
        fields = ['id', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan']


class ResHallWiredPortUpdateForm(ResHallWiredPortCreateForm):

    class Meta:
        fields = ['id', 'switch_ip', 'switch_name', 'blade', 'port', 'vlan']


class AccessPointCreateForm(ACModelForm):
    community = ACModelChoiceField('CommunityAutocomplete')
    building = ACModelChoiceField('BuildingAutocomplete')
    room = ACModelChoiceField('RoomAutocomplete')

    class Media:
        """
        We're currently using Media here, but that forced to move the
        javascript from the footer to the extrahead block ...

        So that example might change when this situation annoys someone a lot.
        """
        js = ('dependant_autocomplete.js',)

    class Meta:
        fields = '__all__'
        autocomplete_fields = ('port')
        model = AccessPoint
