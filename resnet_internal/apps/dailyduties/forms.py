"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: University Housing Internal Daily Duties Forms.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField
from clever_selects.forms import ChainedChoicesForm, ChainedModelChoiceField

from ..core.models import Building, Community


class BuildingSelectForm(ChainedChoicesForm):
    community = ModelChoiceField(queryset=Community.objects.all())
    building = ChainedModelChoiceField('community', reverse_lazy('core_chained_building'), Building)
