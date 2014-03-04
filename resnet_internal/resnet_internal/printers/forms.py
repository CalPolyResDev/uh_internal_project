"""
.. module:: resnet_internal.printers.forms
   :synopsis: ResNet Internal Printer Request Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm
from .models import Printer, Toner, Part


class NewPrinterForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewPrinterForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = Printer
        fields = ('department', 'sub_department', 'printer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description', )


class TonerCountForm(ModelForm):

    class Meta:
        model = Toner
        fields = ('quantity', 'ordered', )


class PartCountForm(ModelForm):

    class Meta:
        model = Part
        fields = ('quantity', 'ordered', )
