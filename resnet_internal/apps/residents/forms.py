"""
.. module:: resnet_internal.apps.residents.forms
   :synopsis: University Housing Internal Resident Lookup Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.forms import ChainedModelChoiceField, ChainedChoicesForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Hidden
from django.core.urlresolvers import reverse_lazy
from django.forms import Form, CharField, ModelChoiceField

from ..core.models import Building, Community


class FullNameSearchForm(Form):
    first_name = CharField(label='First Name', error_messages={'required': 'A first name is required'})
    last_name = CharField(label='Last Name', error_messages={'required': 'A last name is required'})

    def __init__(self, user=None, *args, **kwargs):
        super(FullNameSearchForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-xs-12 text-left'
        self.helper.field_class = 'col-xs-10'

        self.helper.layout = Layout(
            Fieldset(
                'Search by Full Name',
                'first_name',
                'last_name'
            ),
            FormActions(
                Hidden(name="lookup_type", value="full_name"),
                Submit('submit', 'Search'),
            ),
        )


class PrincipalNameSearchForm(Form):
    principal_name = CharField(label='Email Address', max_length=20, error_messages={'required': 'A cal poly email address is required'})

    def __init__(self, user=None, *args, **kwargs):
        super(PrincipalNameSearchForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-xs-12 text-left'
        self.helper.field_class = 'col-xs-10'

        self.helper.layout = Layout(
            Fieldset(
                'Search by Email Address',
                'principal_name',
            ),
            FormActions(
                Hidden(name="lookup_type", value="principal_name"),
                Submit('submit', 'Search'),
            ),
        )


class AddressSearchForm(ChainedChoicesForm):
    community = ModelChoiceField(queryset=Community.objects.all(), label='Community', error_messages={'required': 'A community is required'})
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building, label='Building', error_messages={'required': 'A building is required'})
    room = CharField(label='Room', error_messages={'required': 'A room number is required'})

    def __init__(self, user=None, *args, **kwargs):
        super(AddressSearchForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-xs-12 text-left'
        self.helper.field_class = 'col-xs-10'

        self.helper.layout = Layout(
            Fieldset(
                'Search by Dorm Address',
                'community',
                'building',
                'room'
            ),
            FormActions(
                Hidden(name="lookup_type", value="address"),
                Submit('submit', 'Search'),
            ),
        )
