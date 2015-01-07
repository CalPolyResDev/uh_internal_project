"""
.. module:: resnet_internal.apps.printers.forms
   :synopsis: ResNet Internal Printer Index Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm
from .models import Printer


class PrinterCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PrinterCreateForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

        if "department" in self.fields:
            self.fields["department"].widget.attrs['autocomplete'] = "off"

    class Meta:
        model = Printer
        fields = ['id', 'department', 'sub_department', 'printer_name', 'mac_address', 'ip_address', 'model', 'serial_number', 'property_id', 'description']


class PrinterUpdateForm(PrinterCreateForm):

    class Meta:
        fields = ['id', 'department', 'sub_department', 'printer_name', 'ip_address', 'property_id', 'description']
