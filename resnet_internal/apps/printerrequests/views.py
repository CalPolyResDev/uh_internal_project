"""
.. module:: reslife_internal.printerrequests.views
   :synopsis: ResLife Internal Printer Request Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from .forms import TonerCountForm, PartCountForm
from .models import Request, Toner, Part


logger = logging.getLogger(__name__)


class RequestsListView(ListView):
    """Lists all open printer requests and supplies a form to modify the request status."""

    template_name = "printerrequests/viewrequests.html"

    def get_queryset(self):
        return Request.objects.exclude(status=Request.STATUSES.index('Delivered'))


class InventoryView(TemplateView):
    """Lists inventory for both parts and toner."""

    template_name = "printerrequests/viewinventory.html"
    toner_form = TonerCountForm
    part_form = PartCountForm

    def get_context_data(self, **kwargs):
        context = super(InventoryView, self).get_context_data(**kwargs)

        toner_list = []
        part_list = []

        # Build the toner inventory
        for cartridge in Toner.objects.all():
            list_object = {}
            list_object['cartridge'] = cartridge
            list_object['count_form'] = self.toner_form(instance=cartridge)

            toner_list.append(list_object)

        # Build the part inventory
        for part in Part.objects.all():
            list_object = {}
            list_object['part'] = part
            list_object['count_form'] = self.part_form(instance=part)

            part_list.append(list_object)

        context['toner_list'] = toner_list
        context['part_list'] = part_list

        return context


class OnOrderView(InventoryView):
    """Lists order counts for both parts and toner."""

    template_name = "printerrequests/viewordered.html"
