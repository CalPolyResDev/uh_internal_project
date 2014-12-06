"""
.. module:: resnet_internal.portmap.forms
   :synopsis: ResNet Internal Portmap Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm
from .models import ResHallWired


class ResHallWiredPortCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ResHallWiredPortCreateForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

        if "community" in self.fields:
            self.fields["community"].widget.attrs['autocomplete'] = "off"

    class Meta:
        model = ResHallWired
        fields = ['id', 'community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan']


class ResHallWiredPortUpdateForm(ResHallWiredPortCreateForm):

    class Meta:
        fields = ['id', 'switch_ip', 'switch_name', 'blade', 'port', 'vlan']
