"""
.. module:: resnet_internal.computers.forms
   :synopsis: ResNet Internal Computer Index Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, BooleanField, CharField, ChoiceField, Textarea, ValidationError

from .fields import PortListFormField, DomainNameListFormFiled

PRIORITY_CHOICES = [
    ('Low', 'Low'),  # Not crucial or important; respond as time permits
    ('Medium', 'Medium'),  # Standard problem, question, or request; standard response time acceptable
    ('High', 'High'),  # Important work cannot be completed until ticket is resolved; respond as quickly as possible
    ('Urgent', 'Urgent')  # Time critical work cannot be completed until ticket is resolved. Urgent problems or requests should also be called i
]


class RequestPinholeForm(Form):

    # Request info
    priority = ChoiceField(label=u'Request Priority', choices=PRIORITY_CHOICES)
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
    priority = ChoiceField(label=u'Request Priority', choices=PRIORITY_CHOICES)
    requestor_username = CharField(label=u'Requestor Alias', max_length=25, error_messages={'required': 'A valid requestor is required'})

    # Domain Name info
    domain_names = DomainNameListFormFiled(label=u'Domain Name(s)', widget=Textarea, error_messages={'required': 'At least one domain name must be entered.'})

    def __init__(self, *args, **kwargs):
        super(RequestDomainNameForm, self).__init__(*args, **kwargs)

        self.fields["priority"].choices = PRIORITY_CHOICES
