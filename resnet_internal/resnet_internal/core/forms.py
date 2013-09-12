"""
.. module:: resnet_internal.core.forms
   :synopsis: ResNet Internal Core Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, ChoiceField, RadioSelect

LINK_CHOICES = [
    ('frame', 'in a frame.'),
    ('external', 'in a new tab/window.'),
]


class NavigationSettingsForm(Form):

    handle_links = ChoiceField(label=u'Open links:', widget=RadioSelect)

    def __init__(self, *args, **kwargs):
        super(NavigationSettingsForm, self).__init__(*args, **kwargs)

        self.fields["handle_links"].choices = LINK_CHOICES
