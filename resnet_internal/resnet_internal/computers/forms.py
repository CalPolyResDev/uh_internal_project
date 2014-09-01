"""
.. module:: resnet_internal.computers.forms
   :synopsis: ResNet Internal Computer Index Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, ModelForm, BooleanField, CharField, ChoiceField, Textarea, ValidationError
from srsconnector.models import PRIORITY_CHOICES

from .fields import PortListFormField, DomainNameListFormFiled
from .models import Computer


class NewComputerForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewComputerForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = Computer
        fields = ('department', 'sub_department', 'computer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description', )


class RequestPinholeForm(Form):

    # Request info
    priority = ChoiceField(label=u'Request Priority')
    requestor_username = CharField(label=u'Requestor Alias', max_length=25, error_messages={'required': 'A valid requestor is required'})

    # Pinhole info
    service_name = CharField(label=u'Service Name', max_length=50, error_messages={'required': 'A service name is required'})
    inner_fw = BooleanField(label=u'Inner Firewall', required=False)
    border_fw = BooleanField(label=u'Border Firewall', required=False)
    tcp_ports = PortListFormField(label=u'TCP Ports', max_length=150, required=False)
    udp_ports = PortListFormField(label=u'UDP Ports', max_length=150, required=False)

    def __init__(self, *args, **kwargs):
        super(RequestPinholeForm, self).__init__(*args, **kwargs)

        self.fields["priority"].choices = PRIORITY_CHOICES

    def clean(self):
        cleaned_data = super(RequestPinholeForm, self).clean()

        if cleaned_data["tcp_ports"] == "" and cleaned_data["udp_ports"] == "":
            raise ValidationError("At least one TCP or UDP port must be entered.")
        return cleaned_data


class RequestDomainNameForm(Form):

    # Request info
    priority = ChoiceField(label=u'Request Priority')
    requestor_username = CharField(label=u'Requestor Alias', max_length=25, error_messages={'required': 'A valid requestor is required'})

    # Domain Name info
    domain_names = DomainNameListFormFiled(label=u'Domain Name(s)', widget=Textarea, error_messages={'required': 'At least one domain name must be entered.'})

    def __init__(self, *args, **kwargs):
        super(RequestDomainNameForm, self).__init__(*args, **kwargs)

        self.fields["priority"].choices = PRIORITY_CHOICES
