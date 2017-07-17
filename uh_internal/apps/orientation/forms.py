"""
.. module:: resnet_internal.apps.orientation.forms
   :synopsis: University Housing Internal Orientation Forms.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import os

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, Field, Fieldset, Submit, Reset, Hidden)
from django.forms import Form, CharField, FileField, Textarea, ValidationError


class SRSUploadForm(Form):
    signed_rup = FileField(label="Signed RUP", required=True)

    def __init__(self, *args, **kwargs):
        super(SRSUploadForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Upload your signed RUP (PDF only)',
                Field('signed_rup', placeholder=self.fields['signed_rup'].label),
            ),
            FormActions(
                Submit('submit', 'Upload'),
            ),
        )

    def clean(self):
        cleaned_data = super(SRSUploadForm, self).clean()
        for filedata in cleaned_data:
            if cleaned_data[filedata] is not None:
                name = cleaned_data[filedata].name
                ext = os.path.splitext(name)[1]
                ext = ext.lower()
                if ext != '.pdf':
                    raise ValidationError("The RUP you tried uploading is not a PDF file. It's okay; you're still new here... (love, Alex)")
        return cleaned_data


class OnityEmailForm(Form):
    message = CharField(widget=Textarea, error_messages={'required': 'The message field cannot be left blank.'}, required=True)

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
