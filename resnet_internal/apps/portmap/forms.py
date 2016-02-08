"""
.. module:: resnet_internal.apps.network.forms
   :synopsis: University Housing Internal Network Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.form_fields import ChainedModelChoiceField
from clever_selects.forms import ChainedChoicesModelForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField
from django.forms.models import ModelForm

from ..core.models import Community, Building, Room
from .models import Port, AccessPoint, NetworkInfrastructureDevice


class PortCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
    room = ChainedModelChoiceField('building', reverse_lazy('core_chained_room'), Room)
    upstream_device = ModelChoiceField(queryset=NetworkInfrastructureDevice.objects.all())

    def __init__(self, *args, **kwargs):
        super(PortCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal table-add-form'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Add a new port',
                Field('community', autocomplete='off'),
                Field('building', autocomplete='off'),
                Field('room', autocomplete='off'),
                Field('upstream_device', placeholder=self.fields['upstream_device'].label),
                Field('display_name', placeholder=self.fields['display_name'].label),
                Field('blade_number', placeholder=self.fields['blade_number'].label),
                Field('port_number', placeholder=self.fields['port_number'].label),
            ),
            FormActions(
                Submit('submit', 'Add Port'),
            )
        )

        # Make error messages a bit more readable
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = Port
        fields = ['community', 'building', 'room', 'upstream_device', 'display_name', 'blade_number', 'port_number']


class PortUpdateForm(ModelForm):

    class Meta:
        model = Port
        fields = ['upstream_device', 'blade_number', 'port_number']


class AccessPointCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
    room = ChainedModelChoiceField('building', reverse_lazy('core_chained_room'), Room)
    upstream_device = ChainedModelChoiceField('room', reverse_lazy('ports_chained_port'), Port, label="Port")

    def __init__(self, *args, **kwargs):
        super(AccessPointCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal table-add-form'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Add a new access point',
                Field('community', autocomplete='off'),
                Field('building', autocomplete='off'),
                Field('room', autocomplete='off'),
                Field('upstream_device', autocomplete='off'),
                Field('dns_name', placeholder=self.fields['dns_name'].label),
                Field('property_id', placeholder=self.fields['property_id'].label),
                Field('serial_number', placeholder=self.fields['serial_number'].label),
                Field('mac_address', placeholder=self.fields['mac_address'].label),
                Field('ip_address', placeholder=self.fields['ip_address'].label),
                Field('ap_type', placeholder=self.fields['ap_type'].label),
            ),
            FormActions(
                Submit('submit', 'Add Access Point'),
            )
        )

        # Make error messages a bit more readable
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    def save(self, commit=True):
        access_point = super().save(commit=False)
        access_point.display_name = access_point.dns_name
        if commit:
            access_point.save()
        return access_point

    class Meta:
        model = AccessPoint
        fields = ['community', 'building', 'room', 'upstream_device', 'dns_name', 'property_id', 'serial_number', 'mac_address', 'ip_address', 'ap_type']


class AccessPointUpdateForm(ModelForm):

    def save(self, commit=True):
        access_point = super().save(commit=False)
        access_point.display_name = access_point.dns_name
        if commit:
            access_point.save()
        return access_point

    class Meta:
        model = AccessPoint
        fields = ['dns_name', 'property_id', 'serial_number', 'mac_address', 'ip_address', 'ap_type']
