"""
.. module:: resnet_internal.apps.printerrequests.forms
   :synopsis: University Housing Internal Printer Request Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms.fields import ChoiceField, BooleanField
from django.forms.forms import Form
from django.forms.models import ModelForm, ModelChoiceField
from srsconnector.models import PRIORITY_CHOICES

from .models import PrinterType, Toner, Part


class TonerRequestForm(Form):

    def __init__(self, *args, **kwargs):
        super(TonerRequestForm, self).__init__(*args, **kwargs)

        # Ticket info
        self.priority = ChoiceField(label='Request Priority', error_messages={'required': 'Please select a priority'})

        # Request info
        self.printer = ModelChoiceField(queryset=PrinterType.objects.all(), empty_label="-------------", label='Printer', error_messages={'required': 'Please select a printer'})
        self.toner = ChoiceField(label='Color', error_messages={'required': 'Please select a color'})
        self.for_front_desk = BooleanField(label='For front desk?', initial=False, required=False)

        self.fields["priority"].choices = PRIORITY_CHOICES
        self.fields["toner"].choices.extend([(str(toner.id), toner.color) for toner in Toner.objects.all()])


class PartsRequestForm(Form):

    def __init__(self, *args, **kwargs):
        super(PartsRequestForm, self).__init__(*args, **kwargs)

        # Ticket info
        self.priority = ChoiceField(label='Request Priority', error_messages={'required': 'Please select a priority'})

        # Request info
        self.queryset = PrinterType.objects.filter(id__in=set(Part.objects.values_list('printer', flat=True)))
        self.printer = ModelChoiceField(queryset=self.queryset, empty_label="-------------", label='Printer', error_messages={'required': 'Please select a printer'})
        self.part = ChoiceField(label='Part', error_messages={'required': 'Please select a part'})

        self.fields["priority"].choices = PRIORITY_CHOICES
        self.fields["part"].choices.extend([(str(part.id), part.type) for part in Part.objects.all()])


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
