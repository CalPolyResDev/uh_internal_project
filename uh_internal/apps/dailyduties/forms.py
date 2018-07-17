"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: University Housing Internal Daily Duties Forms.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from clever_selects.forms import ChainedChoicesForm, ChainedModelChoiceField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset
from django.forms import ModelChoiceField
from django.urls import reverse_lazy

from ..core.models import Building, Community


class BuildingSelectForm(ChainedChoicesForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core:chained_building'), Building)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

#         self.helper.form_class = 'form-vertical'

        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('community', autocomplete='off'),
                Field('building', autocomplete='off'),
            ),
        )
