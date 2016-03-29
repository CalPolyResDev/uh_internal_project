"""
.. module:: resnet_internal.technicians.forms
   :synopsis: University Housing Internal Technicians Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit
from django.forms import Form, CharField

from .validators import validate_ad_membership


class AddADUserForm(Form):
    principal_name = CharField(label='Cal Poly Email Address', max_length=26, error_messages={'required': 'An email address is required.'}, validators=[validate_ad_membership])

    def __init__(self, *args, **kwargs):
        super(AddADUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal table-add-form'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Add a new technician',
                Field('principal_name', placeholder=self.fields['principal_name'].label),
            ),
            FormActions(
                Submit('submit', 'Add Technician'),
            )
        )
