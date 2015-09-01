"""
.. module:: resnet_internal.apps.core.forms
   :synopsis: ResNet Internal Core Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.contrib.auth.forms import AuthenticationForm
from django.forms import Form, ChoiceField, RadioSelect


LINK_CHOICES = [
    ('frame', 'in a frame.'),
    ('external', 'in a new tab/window.'),
]


class AutoFocusAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AutoFocusAuthenticationForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs['autofocus'] = True


class NavigationSettingsForm(Form):

    handle_links = ChoiceField(label='Open links:', widget=RadioSelect)

    def __init__(self, *args, **kwargs):
        super(NavigationSettingsForm, self).__init__(*args, **kwargs)

        self.fields["handle_links"].choices = LINK_CHOICES
