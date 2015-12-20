"""
.. module:: resnet_internal.apps.printers.forms
   :synopsis: ResNet Internal Printer Index Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.form_fields import ChainedModelChoiceField
from clever_selects.forms import ChainedChoicesModelForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, HTML
from django.core.urlresolvers import reverse_lazy

from ..core.models import SubDepartment
from .models import Printer


class PrinterForm(ChainedChoicesModelForm):
    sub_department = ChainedModelChoiceField('department', reverse_lazy('core_chained_sub_department'), SubDepartment, label="Sub Department")

    def __init__(self, *args, **kwargs):
        super(PrinterForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal table-add-form'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        submit_button = Submit('submit', 'Add Printer')
        submit_button.field_classes = 'btn btn-primary'

        self.helper.layout = Layout(
            Fieldset(
                'Add a new printer',
                Field('department', autocomplete='off'),
                Field('sub_department', autocomplete='off'),
                Field('printer_name', placeholder=self.fields['printer_name'].label),
                Field('mac_address', placeholder=self.fields['mac_address'].label),
                Field('ip_address', css_class="ip_address_field", placeholder=self.fields['ip_address'].label),
                Field('model', placeholder=self.fields['model'].label),
                Field('serial_number', placeholder=self.fields['serial_number'].label),
                Field('property_id', placeholder=self.fields['property_id'].label),
                Field('location', placeholder=self.fields['location'].label),
                Field('date_purchased', css_class="dateinput", placeholder=self.fields['date_purchased'].label),
                Field('description', placeholder=self.fields['description'].label),
            ),
            FormActions(submit_button)
        )

        self.fields["date_purchased"].widget.attrs['class'] = "dateinput"

        # Make error messages a bit more readable
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = Printer
        fields = ['department', 'sub_department', 'printer_name', 'mac_address', 'ip_address', 'model', 'serial_number', 'property_id', 'location', 'date_purchased', 'description']
