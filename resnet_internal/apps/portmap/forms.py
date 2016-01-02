"""
.. module:: resnet_internal.apps.portmap.forms
   :synopsis: University Housing Internal Port Map Forms.

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
from .models import Port, AccessPoint


class PortCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
    room = ChainedModelChoiceField('building', reverse_lazy('core_chained_room'), Room)

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
                Field('switch_ip', placeholder=self.fields['switch_ip'].label),
                Field('switch_name', placeholder=self.fields['switch_name'].label),
                Field('jack', placeholder=self.fields['jack'].label),
                Field('blade', placeholder=self.fields['blade'].label),
                Field('port', placeholder=self.fields['port'].label),
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
        fields = ['community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port']


class PortUpdateForm(ModelForm):

    class Meta:
        model = Port
        fields = ['switch_ip', 'switch_name', 'blade', 'port']


class AccessPointCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
    room = ChainedModelChoiceField('building', reverse_lazy('core_chained_room'), Room)
    port = ChainedModelChoiceField('room', reverse_lazy('portmap_chained_port'), Port, label="Jack")

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
                Field('port', autocomplete='off'),
                Field('name', placeholder=self.fields['name'].label),
                Field('property_id', placeholder=self.fields['property_id'].label),
                Field('serial_number', placeholder=self.fields['serial_number'].label),
                Field('mac_address', placeholder=self.fields['mac_address'].label),
                Field('ip_address', placeholder=self.fields['ip_address'].label),
                Field('ap_type', placeholder=self.fields['ap_type'].label),
            ),
            FormActions(
                Submit('submit', 'Add Port'),
            )
        )

        # Make error messages a bit more readable
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = AccessPoint
        fields = ['community', 'building', 'room', 'port', 'name', 'property_id', 'serial_number', 'mac_address', 'ip_address', 'ap_type']


class AccessPointUpdateForm(ModelForm):

    class Meta:
        model = AccessPoint
        fields = ['name', 'property_id', 'serial_number', 'mac_address', 'ip_address', 'ap_type']
