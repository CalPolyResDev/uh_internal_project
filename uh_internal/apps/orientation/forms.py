"""
.. module:: resnet_internal.apps.orientation.forms
   :synopsis: University Housing Internal Orientation Forms.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import os

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, Field, Fieldset, Submit, Reset, Hidden)
from django.forms import Form, CharField, Textarea, ValidationError


class SRSUploadForm(Form):

    def __init__(self, *args, **kwargs):
        super(SRSUploadForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            FormActions(
                Submit('submit', 'Submit'),
            ),
        )


class OnityEmailForm(Form):
    message = CharField(widget=Textarea,
                        error_messages={'required': 'The message field cannot be left blank.'},
                        required=True)

    def __init__(self, *args, **kwargs):
        super(OnityEmailForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Send an email (optional)',
                Field('message', placeholder=self.fields['message'].label),
                Hidden('to_email', '{{ onity_staff_email }}'),
            ),
            FormActions(
                Submit('submit', 'Send'),
                Reset('reset', 'Reset'),
            ),
        )
