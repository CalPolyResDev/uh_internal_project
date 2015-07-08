"""
.. module:: resnet_internal.apps.printerrequests.forms
   :synopsis: ResNet Internal Printer Request Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm
from .models import Toner, Part


class TonerCountForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(TonerCountForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autocomplete'] = "off"

    class Meta:
        model = Toner
        fields = ('quantity', 'ordered', )


class PartCountForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartCountForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autocomplete'] = "off"

    class Meta:
        model = Part
        fields = ('quantity', 'ordered', )
