"""
.. module:: resnet_internal.apps.portmap.forms
   :synopsis: ResNet Internal Portmap Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.forms import ChainedChoicesModelForm, ChainedModelChoiceField
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField, ModelForm

from ..core.models import Community, Building, Room
from .models import ResHallWired, AccessPoint


class ResHallWiredPortCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
    room = ChainedModelChoiceField('building', reverse_lazy('core_chained_room'), Room)

    def __init__(self, *args, **kwargs):
        super(ResHallWiredPortCreateForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = ResHallWired
        fields = ['id', 'community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan']


class ResHallWiredPortUpdateForm(ModelForm):

    class Meta:
        model = ResHallWired
        fields = ['id', 'switch_ip', 'switch_name', 'blade', 'port', 'vlan']


class AccessPointCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all(), required=True)
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
    room = ChainedModelChoiceField('building', reverse_lazy('core_chained_room'), Room)
    port = ChainedModelChoiceField('room', reverse_lazy('portmap_chained_port'), ResHallWired)

    class Meta:
        model = AccessPoint
        fields = ['name', 'property_id', 'serial_number', 'mac_address', 'ip_address', 'type', 'community', 'building', 'room', 'port']
