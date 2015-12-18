"""
.. module:: resnet_internal.apps.computers.forms
   :synopsis: ResNet Internal Computer Index Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.form_fields import ChainedModelChoiceField
from clever_selects.forms import ChainedChoicesModelForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, HTML
from django.core.urlresolvers import reverse_lazy
from django.forms import Form, BooleanField, CharField, ChoiceField, Textarea, ValidationError
from srsconnector.models import PRIORITY_CHOICES

from ..core.models import SubDepartment
from .fields import PortListFormField, DomainNameListFormFiled
from .models import Computer

IP_REQUEST_INFORMATION = """<p>When this form is submitted, a service request will be created in your name and sent to NetAdmin.<br />
        The service request ID will show up next to the newly created domain name record for your reference.<br />
        Multiple domain names must be separated by commas and no whitespace..</p>
        <p style="color: red;">NOTE: If you are unsure if you are a valid requestor, check first. Sending a request without proper permissions wastes everyone's time.</p><br />"""


class ComputerForm(ChainedChoicesModelForm):
    sub_department = ChainedModelChoiceField('department', reverse_lazy('core_chained_sub_department'), SubDepartment, label="Sub Department")

    def __init__(self, *args, **kwargs):
        super(ComputerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal table-add-form'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        submit_button = Submit('submit', 'Add Computer')
        submit_button.field_classes = 'btn btn-primary'

        self.helper.layout = Layout(
            Fieldset(
                'Add a new computer',
                Field('department', autocomplete='off'),
                Field('sub_department', autocomplete='off'),
                Field('computer_name', placeholder=self.fields['computer_name'].label),
                Field('mac_address', placeholder=self.fields['mac_address'].label),
                Field('ip_address', css_class="ip_address_field", placeholder=self.fields['ip_address'].label),
                Field('model', placeholder=self.fields['model'].label),
                Field('serial_number', placeholder=self.fields['serial_number'].label),
                Field('property_id', placeholder=self.fields['property_id'].label),
                Field('location', placeholder=self.fields['location'].label),
                Field('date_purchased', css_class="dateinput", placeholder=self.fields['date_purchased'].label),
                Field('dn', placeholder=self.fields['dn'].label),
                Field('description', placeholder=self.fields['description'].label),
            ),
            FormActions(submit_button)
        )

        self.fields["date_purchased"].widget.attrs['class'] = "dateinput"

        # Make error messages a bit more readable
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    def clean_dn(self):
        data = self.cleaned_data['dn']
        dn_pieces = data.split(",")
        stripped_dn_pieces = []

        for dn_piece in dn_pieces:
            try:
                group_type, group_string = dn_piece.split("=")
            except ValueError:
                self.add_error("dn", ValidationError("Please enter a valid DN."))
                return data

            stripped_dn_pieces.append('%(type)s=%(string)s' % {'type': group_type.strip(), 'string': group_string.strip()})

        return ', '.join(stripped_dn_pieces)

    class Meta:
        model = Computer
        fields = ['department', 'sub_department', 'computer_name', 'mac_address', 'ip_address', 'model', 'serial_number', 'property_id', 'location', 'date_purchased', 'dn', 'description']


class RequestPinholeForm(Form):

    # Request info
    priority = ChoiceField(label='Request Priority')
    requestor_username = CharField(label='Requestor Alias', max_length=25, error_messages={'required': 'A valid requestor is required'})

    # Pinhole info
    service_name = CharField(label='Service Name', max_length=50, error_messages={'required': 'A service name is required'})
    inner_fw = BooleanField(label='Inner Firewall', required=False)
    border_fw = BooleanField(label='Border Firewall', required=False)
    tcp_ports = PortListFormField(label='TCP Ports', max_length=150, required=False)
    udp_ports = PortListFormField(label='UDP Ports', max_length=150, required=False)

    def __init__(self, *args, **kwargs):
        super(RequestPinholeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'

        submit_button = Submit('submit', 'Submit')
        submit_button.field_classes = 'btn btn-primary'

        self.helper.layout = Layout(
            Fieldset(
                'Request a Pinhole',
                HTML(IP_REQUEST_INFORMATION),

                HTML("""<br /><i>Request Information</i><hr />"""),
                Field('priority', placeholder=self.fields['priority'].label),
                Field('requestor_username', placeholder=self.fields['requestor_username'].label),

                HTML("""<br /><i>Pinhole Information</i><hr />"""),
                Field('service_name', placeholder=self.fields['service_name'].label),
                Field('inner_fw'),
                Field('border_fw'),
                Field('tcp_ports', placeholder=self.fields['tcp_ports'].label),
                Field('udp_ports', placeholder=self.fields['udp_ports'].label),
            ),
            FormActions(submit_button)
        )

        self.fields["priority"].choices = PRIORITY_CHOICES

    def clean(self):
        cleaned_data = super(RequestPinholeForm, self).clean()

        if cleaned_data["tcp_ports"] == "" and cleaned_data["udp_ports"] == "":
            raise ValidationError("At least one TCP or UDP port must be entered.")

        if cleaned_data["inner_fw"] is False and cleaned_data["border_fw"] is False:
            raise ValidationError("At least one firewall must be selected.")
        return cleaned_data


class RequestDomainNameForm(Form):

    # Request info
    priority = ChoiceField(label='Request Priority')
    requestor_username = CharField(label='Requestor Alias', max_length=25, error_messages={'required': 'A valid requestor is required'})

    # Domain Name info
    domain_names = DomainNameListFormFiled(label='Domain Name(s)', widget=Textarea, error_messages={'required': 'At least one domain name must be entered.'})

    def __init__(self, *args, **kwargs):
        super(RequestDomainNameForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'

        submit_button = Submit('submit', 'Submit')
        submit_button.field_classes = 'btn btn-primary'
        self.helper.layout = Layout(
            Fieldset(
                'Request a Domain Name (CNAME)',
                HTML(IP_REQUEST_INFORMATION),
                Field('priority', placeholder=self.fields['priority'].label),
                Field('requestor_username', placeholder=self.fields['requestor_username'].label),
                Field('domain_names', placeholder=self.fields['domain_names'].label),
            ),
            FormActions(submit_button)
        )

        self.fields["priority"].choices = PRIORITY_CHOICES
