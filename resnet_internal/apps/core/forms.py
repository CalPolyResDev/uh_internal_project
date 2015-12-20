"""
.. module:: resnet_internal.apps.core.forms
   :synopsis: ResNet Internal Core Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.forms import ChainedChoicesModelForm, ChainedModelChoiceField
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField, ModelForm

from .models import Community, Building, Room


class RoomCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)

    def __init__(self, *args, **kwargs):
        super(RoomCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal table-add-form'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Add a new room',
                Field('community', autocomplete='off'),
                Field('building', autocomplete='off'),
                Field('name', placeholder=self.fields['name'].label),
            ),
            FormActions(
                Submit('submit', 'Add Room'),
            )
        )

    class Meta:
        model = Room
        fields = ['community', 'building', 'name']


class RoomUpdateForm(ModelForm):

    class Meta:
        model = Room
        fields = ['name']
