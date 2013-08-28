"""
.. module:: resnet_internal.orientation.forms
   :synopsis: ResNet Internal Orientation Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import os

from django.forms import Form, CharField, FileField, Textarea, ValidationError


class SRSUploadForm(Form):
    signed_rup = FileField(required=True)

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
