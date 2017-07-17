"""
.. module:: resnet_internal.printers.views
   :synopsis: University Housing Internal Printer Index Views.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import logging

from django.core.urlresolvers import reverse_lazy

from ..datatables.views import DatatablesView
from .ajax import PopulatePrinters
from .forms import PrinterForm
from .models import Printer


logger = logging.getLogger(__name__)


class PrintersView(DatatablesView):
    template_name = "printers/printers.djhtml"
    model = Printer
    form_class = PrinterForm
    populate_class = PopulatePrinters
    success_url = reverse_lazy('printers:home')
