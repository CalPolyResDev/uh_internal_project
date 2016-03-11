"""
.. module:: resnet_internal.printerrequests.views
   :synopsis: University Housing Internal Printer Request Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import TonerCountForm, PartCountForm
from .models import Request, Toner, Part


logger = logging.getLogger(__name__)


class RequestTonerView(FormView):
    """Creates a service request for printer toner."""

    template_name = "printers/request_toner.html"
    form_class = TonerRequestForm
    success_url = reverse_lazy('printer_request_list')

    def form_valid(self, form):
        priority = form.cleaned_data['priority']
        printer = form.cleaned_data['printer']  # Returns a printer object, since ModelChoiceField was used
        toner_id = form.cleaned_data['toner']
        for_front_desk = form.cleaned_data['for_front_desk']

        toner = Toner.objects.get(id=toner_id)
        request_list = [toner]
        requestor_alias = self.request.user.get_alias()

        # Create the service request
        toner_service_request = PrinterRequest()
        toner_service_request.priority = priority
        toner_service_request.requestor_username = requestor_alias
        toner_service_request.printer_model = printer.model
        toner_service_request.printer_manufacturer = printer.make
        toner_service_request.request_type = '**TONER_REQUEST'
        toner_service_request.request_list = request_list
        toner_service_request.work_log = 'Created Ticket for %s.' % requestor_alias

        toner_service_request.save()

        # Create the resnet request.
        toner_request = Request()
        toner_request.ticket_id = toner_service_request.ticket_id
        toner_request.date_requested = datetime.now()
        toner_request.priority = priority
        toner_request.requestor = requestor_alias

        # Determine where to send it
        try:
            address = CSDMapping.objects.get(csd_alias=requestor_alias).csd_domain + " " + ("Front Desk" if for_front_desk else "CSD Office")
        except CSDMapping.DoesNotExist:
            updated_toner_service_request = PrinterRequest.objects.get(ticket_id=toner_service_request.ticket_id)
            address = "Building " + updated_toner_service_request.requestor_building + " Room " + updated_toner_service_request.requestor_room

        toner_request.address = address
        toner_request.status = Request.STATUSES.index("Open")

        toner_request.save()
        toner_request.add_toner(request_list)

        return super(RequestTonerView, self).form_valid(form)


class RequestPartsView(FormView):
    """Creates a service request for printer parts."""

    template_name = "printers/request_part.html"
    form_class = PartsRequestForm
    success_url = reverse_lazy('printer_request_list')

    def form_valid(self, form):
        priority = form.cleaned_data['priority']
        printer = form.cleaned_data['printer']  # Returns a printer object, since ModelChoiceField was used
        part_id = form.cleaned_data['part']

        part = Part.objects.get(id=part_id)
        request_list = [part]
        requestor_alias = self.request.user.get_alias()

        # Create the service request
        part_service_request = PrinterRequest()
        part_service_request.priority = priority
        part_service_request.requestor_username = requestor_alias
        part_service_request.printer_model = printer.model
        part_service_request.printer_manufacturer = printer.make
        part_service_request.request_type = '**PARTS_REQUEST'
        part_service_request.request_list = request_list
        part_service_request.work_log = 'Created Ticket for %s.' % requestor_alias

        part_service_request.save()

        # Create the resnet request.
        part_request = Request()
        part_request.ticket_id = part_service_request.ticket_id
        part_request.date_requested = datetime.now()
        part_request.priority = priority
        part_request.requestor = requestor_alias

        part_request.address = address
        part_request.status = Request.STATUSES.index("Open")

        part_request.save()
        part_request.add_parts(request_list)

        return super(RequestPartsView, self).form_valid(form)


class RequestsListView(ListView):
    """Lists all open printer requests and supplies a form to modify the request status."""

    template_name = "printerrequests/viewrequests.html"

    def get_queryset(self):
        query = Request.objects.exclude(status=Request.STATUSES.index('Delivered'))

        if self.request.user.has_access(TECHNICIAN_ACCESS):
            query = query.filter(requestor=self.request.user.get_alias())

        return query


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
