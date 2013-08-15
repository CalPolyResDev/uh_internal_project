from django import forms
import os

#
# ResNet Internal Orientation forms
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

class SRSUploadForm(forms.Form):
    signed_rup = forms.FileField(required=True)

    def clean(self):
        cleaned_data = super(SRSUploadForm, self).clean()
        for filedata in cleaned_data:
            if cleaned_data[filedata] is not None:
                name = cleaned_data[filedata].name
                ext = os.path.splitext(name)[1]
                ext = ext.lower()
                if ext != '.pdf':
                    raise forms.ValidationError("The RUP you tried uploading is not a PDF file. It's okay; you're still new here... (love, Alex)")
        return cleaned_data

class OnityEmailForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, error_messages={'required': 'The message field cannot be left blank.'}, required=True)
