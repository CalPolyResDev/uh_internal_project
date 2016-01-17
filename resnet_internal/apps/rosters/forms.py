"""
.. module:: reslife_internal.apps.rosters.forms
   :synopsis: University Housing Internal Roster Generator Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Hidden
from django.forms import Form

from ..core.models import Building, CSDMapping
from .fields import RosterBuildingChoiceField


class GenerationForm(Form):
    buildings = RosterBuildingChoiceField(queryset=Building.objects.all().order_by("community"))

    def __init__(self, user=None, *args, **kwargs):
        super(GenerationForm, self).__init__(*args, **kwargs)

        # Set selected
        if user:
            try:
                csd_mapping = CSDMapping.objects.get(email=user.email)
            except CSDMapping.DoesNotExist:
                pass
            else:
                self.initial['buildings'] = csd_mapping.buildings.all()

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10 col-md-8'

        self.helper.layout = Layout(
            Fieldset(
                'Select buildings',
                Field('buildings', style="height: 40vh;"),
            ),
            FormActions(
                Hidden(name="mode", value="", css_id="id_mode"),
                Submit('submit', 'Generate', onclick="$('#id_mode').val('normal'); block_ui(); return true;"),
                Submit('submit', 'Generate CSV', onclick="$('#id_mode').val('csv'); block_ui(); return true;"),
            ),
        )
