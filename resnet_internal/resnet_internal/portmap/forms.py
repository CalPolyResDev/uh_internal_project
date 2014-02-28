"""
.. module:: resnet_internal.printers.forms
   :synopsis: ResNet Internal Printer Request Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm
from .models import ResHallWired


class NewPortForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewPortForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = ResHallWired
        fields = ('community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan', )
