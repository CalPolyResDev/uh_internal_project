"""
.. module:: resnet_internal.printers.forms
   :synopsis: ResNet Internal Printer Request Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm
from .models import Toner, Part


class TonerCountForm(ModelForm):

    class Meta:
        model = Toner
        fields = ('quantity', 'ordered', )


class PartCountForm(ModelForm):

    class Meta:
        model = Part
        fields = ('quantity', 'ordered', )