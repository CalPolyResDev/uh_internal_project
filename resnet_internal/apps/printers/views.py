"""
.. module:: reslife_internal.printers.views
   :synopsis: ResLife Internal Printer Index Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.core.urlresolvers import reverse_lazy

from ..datatables.views import DatatablesView
from .ajax import PopulatePrinters
from .forms import PrinterForm
from .models import Printer


logger = logging.getLogger(__name__)


class PrintersView(DatatablesView):
    template_name = "printers/printers.html"
    model = Printer
    form_class = PrinterForm
    populate_class = PopulatePrinters
    success_url = reverse_lazy('printers')
