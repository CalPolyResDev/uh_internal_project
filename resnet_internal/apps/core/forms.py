"""
.. module:: resnet_internal.apps.core.forms
   :synopsis: ResNet Internal Core Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.forms import ChainedChoicesModelForm, ChainedModelChoiceField

from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField, ModelForm

from .models import Community, Building, Room


class AutoFocusAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AutoFocusAuthenticationForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs['autofocus'] = True

    def clean_username(self):
        """Trim the @calpoly.edu if it's entered."""

        username = self.cleaned_data["username"]
        return username.replace("@calpoly.edu", "")


class RoomCreateForm(ChainedChoicesModelForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)

    class Meta:
        model = Room
        fields = ['name', 'community', 'building']


class RoomUpdateForm(ModelForm):

    class Meta:
        model = Room
        fields = ['name']
