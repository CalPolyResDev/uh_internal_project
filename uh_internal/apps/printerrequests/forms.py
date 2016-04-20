"""
.. module:: resnet_internal.apps.printerrequests.forms
   :synopsis: University Housing Internal Printer Request Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.form_fields import ChainedModelChoiceField
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django.core.urlresolvers import reverse_lazy
from django.forms.fields import ChoiceField, CharField
from django.forms.forms import Form
from django.forms.models import ModelForm, ModelChoiceField
from srsconnector.models import PRIORITY_CHOICES

from .models import PrinterType, Toner, Part


class TonerRequestForm(Form):
    # Ticket info
    priority = ChoiceField(label='Request Priority', error_messages={'required': 'Please select a priority'})

    # Request info
    printer = ModelChoiceField(queryset=PrinterType.objects.all(), empty_label="-------------", label='Printer', error_messages={'required': 'Please select a printer'})
    toner = ChainedModelChoiceField('printer', reverse_lazy('printerrequests:chained_toner'), Toner, label='Color', error_messages={'required': 'Please select a color'})
    address = CharField(label='Location')

    def __init__(self, *args, **kwargs):
        super(TonerRequestForm, self).__init__(*args, **kwargs)

        self.fields["priority"].choices = PRIORITY_CHOICES

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8 col-md-6'

        self.helper.layout = Layout(
            Fieldset(
                'Create a toner request',
                *self.fields
            ),
            FormActions(
                Submit('submit', 'Submit'),
            )
        )


class PartsRequestForm(Form):
    # Ticket info
    priority = ChoiceField(label='Request Priority', error_messages={'required': 'Please select a priority'})

    # Request info
    printer = ModelChoiceField(queryset=None, empty_label="-------------", label='Printer', error_messages={'required': 'Please select a printer'})
    part = ChainedModelChoiceField('printer', reverse_lazy('printerrequests:chained_part'), Part, label='Part', error_messages={'required': 'Please select a part'})
    address = CharField(label='Location')

    def __init__(self, *args, **kwargs):
        super(PartsRequestForm, self).__init__(*args, **kwargs)

        self.fields['printer'].queryset = PrinterType.objects.filter(id__in=set(Part.objects.values_list('printer', flat=True)))
        self.fields["priority"].choices = PRIORITY_CHOICES

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8 col-md-6'

        self.helper.layout = Layout(
            Fieldset(
                'Create a parts request',
                *self.fields
            ),
            FormActions(
                Submit('submit', 'Submit'),
            )
        )


class TonerCountForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(TonerCountForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autocomplete'] = "off"

    class Meta:
        model = Toner
        fields = ('quantity', 'ordered',)


class PartCountForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartCountForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autocomplete'] = "off"

    class Meta:
        model = Part
        fields = ('quantity', 'ordered',)
