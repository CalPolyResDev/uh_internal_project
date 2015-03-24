"""
.. module:: resnet_internal.apps.computers.forms
   :synopsis: ResNet Internal Computer Index Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, ModelForm, BooleanField, CharField, ChoiceField, Textarea, ValidationError
from srsconnector.models import PRIORITY_CHOICES

from .fields import PortListFormField, DomainNameListFormFiled
from .models import Computer


class ComputerCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ComputerCreateForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

        if "department" in self.fields:
            self.fields["department"].widget.attrs['autocomplete'] = "off"

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
        fields = ['id', 'department', 'sub_department', 'computer_name', 'mac_address', 'ip_address', 'model', 'serial_number', 'property_id', 'location', 'dn', 'description']


class ComputerUpdateForm(ComputerCreateForm):
    pass


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

        self.fields["priority"].choices = PRIORITY_CHOICES
