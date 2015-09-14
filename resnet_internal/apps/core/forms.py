"""
.. module:: resnet_internal.apps.core.forms
   :synopsis: ResNet Internal Core Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.contrib.auth.forms import AuthenticationForm


class AutoFocusAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AutoFocusAuthenticationForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs['autofocus'] = True

    def clean_username(self):
        """Trim the @calpoly.edu if it's entered."""

        username = self.cleaned_data["username"]
        return username.replace("@calpoly.edu", "")
