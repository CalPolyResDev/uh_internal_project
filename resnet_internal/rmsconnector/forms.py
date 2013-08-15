"""
.. module:: rmsconnector.forms
   :synopsis: RMS Connector Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.contrib.auth import authenticate
from django import forms


class RMSAuthenticationForm(forms.Form):
    alias = forms.CharField(label='Cal Poly Alias', max_length=8, error_messages={'required': 'A username is required'})
    dob = forms.DateField(label='Birth Date (mm/dd/YYYY)', input_formats=['%m/%d/%Y'], error_messages={'required': 'A date of birth is required', 'invalid': 'Invalid date format. Use mm/dd/YYYY'})

    error_messages = {
        'invalid_login': u"Please enter a correct username and date of birth. "
                          "Note that the username is case-sensitive.",
        'no_cookies': u"Your Web browser doesn't appear to have cookies "
                       "enabled. Cookies are required for logging in.",
        'inactive': u"This account is inactive.",
    }

    def clean(self):
        cleaned_data = super(RMSAuthenticationForm, self).clean()
        alias = cleaned_data.get('alias')
        dob = cleaned_data.get('dob')

        if alias and dob:
            user = authenticate(alias=alias, dob=dob)
            if user is None:
                del cleaned_data["dob"]
                raise forms.ValidationError(self.error_messages['invalid_login'])
            elif not user.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])

        return cleaned_data
