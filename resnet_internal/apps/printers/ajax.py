"""
.. module:: resnet_internal.apps.printers.ajax
   :synopsis: ResNet Internal Printers AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict

from django.core.urlresolvers import reverse, reverse_lazy
from django.http.response import HttpResponseRedirect
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax
from srsconnector.models import STATUS_CHOICES, PrinterRequest

from ...settings.base import printers_modify_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView
from .models import Printer, Request, Toner, Part
from .forms import PrinterUpdateForm
from .utils import can_fulfill_request, send_replenishment_email, send_delivery_confirmation


class PopulatePrinters(RNINDatatablesPopulateView):
    """Renders the printer index."""

    table_name = "printer_index"
    data_source = reverse_lazy('populate_uh_printers')
    update_source = reverse_lazy('update_uh_printer')
    model = Printer

    # NOTE Installed Types: ip-address, mac-address

    column_definitions = OrderedDict()
    column_definitions["id"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "ID"}
    column_definitions["department"] = {"width": "225px", "type": "string", "title": "Department"}
    column_definitions["sub_department"] = {"width": "225px", "type": "string", "title": "Sub Department"}
    column_definitions["printer_name"] = {"width": "150px", "type": "string", "title": "Printer Name"}
    column_definitions["mac_address"] = {"width": "150px", "type": "mac-address", "editable": False, "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "ip-address", "title": "IP Address"}
    column_definitions["model"] = {"width": "100px", "type": "string", "editable": False, "title": "Model"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "editable": False, "title": "Serial Number"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["description"] = {"width": "225px", "type": "string", "className": "edit_trigger", "title": "Description"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"] = {"width": "50px", "type": "string", "searchable": False, "orderable": False, "editable": False, "title": "&nbsp;"}

        return super(PopulatePrinters, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = printers_modify_access_test(user)

    def render_column(self, row, column):
        if column == 'remove':
            onclick = "confirm_remove({id});return false;".format(id=row.id)
            link_block = self.link_block_template.format(link_url="", onclick_action=onclick, link_target="", link_class_name="", link_style="color:red; cursor:pointer;", link_text="Remove")

            return self.base_column_template.format(id=row.id, class_name="", column=column, value="", link_block=link_block, inline_images="", editable_block="")
        else:
            return super(PopulatePrinters, self).render_column(row, column)


class UpdatePrinter(BaseDatatablesUpdateView):
    form_class = PrinterUpdateForm
    model = Printer
    populate_class = PopulatePrinters


@ajax
@require_POST
def remove_printer(request):
    """ Removes printers from the printer index.

    :param printer_id: The printer's id.
    :type printer_id: str

    """

    # Pull post parameters
    printer_id = request.POST["printer_id"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["printer_id"] = printer_id

    printer_instance = Printer.objects.get(id=printer_id)
    printer_instance.delete()

    return context


@ajax
@require_POST
def change_request_status(request):
    """ Updates the status of a printer request based on a drop-down value.

    :param request_id: The id of the request to process.
    :type request_id: str
    :param current_status: The new status value.
    :type status: str

    """

    # Pull post parameters
    request_id = request.POST["request_id"]
    current_status = request.POST["current_status"]

    context = {}
    context["success"] = True
    context["error_message"] = None

    send_replenishment_email()

    status = int(current_status) + 1

    STATUS_MAP = {
        Request.STATUSES.index('Acknowledged'): 'Work In Progress',
        Request.STATUSES.index('Delivered'): 'Closed',
    }

    request_instance = Request.objects.get(id=request_id)

    if status in STATUS_MAP:
        # Handle inventory decrementation for acknowledge requests
        if status == Request.STATUSES.index('Acknowledged'):
            if can_fulfill_request(request_id):
                # Decrement each cartridge quantity
                for cartridge in request_instance.toner.all():
                    cartridge.quantity = cartridge.quantity - 1
                    cartridge.save()

                # Decrement each part quantity
                for part in request_instance.parts.all():
                    part.quantity = part.quantity - 1
                    part.save()
            else:
                context["success"] = False
                context["error_message"] = "Cannot acknowledge request: Insufficient Inventory."
                return context

        # Update the SRS ticket
        ticket = PrinterRequest.objects.get(ticket_id=request_instance.ticket_id)

        # Grab the correct value for the srs ticket status
        ticket_status = STATUS_MAP[status]
        for choice in STATUS_CHOICES:
            if ticket_status in choice:
                srs_status_value = choice[1]  # The status won't accept the int values

        ticket.status = srs_status_value

        if status == Request.STATUSES.index('Delivered'):
            ticket.solution = "Item delivered by %s." % request.user.get_full_name()
            send_delivery_confirmation(request_instance)

        request_list = []

        if "TONER" in ticket.request_type:
            for cartridge in request_instance.toner.all():
                request_list.append(cartridge)
        elif "PARTS" in ticket.request_type:
            for part in request_instance.parts.all():
                request_list.append(part)

        ticket.request_list = request_list  # Must include in update; gets blanked otherwise
        ticket.work_log = "Ticket status updated to %s by %s." % (Request.STATUSES[status], request.user.get_full_name())
        ticket.save()

    request_instance.status = status
    request_instance.save()

    return HttpResponseRedirect(reverse('printer_request_list'))


@ajax
@require_POST
def update_toner_inventory(request):
    """ Updates the inventory quantity of a toner cartridge.

    :param toner_id: The id of the toner cartridge to process.
    :type toner_id: str
    :param quantity: The updated quantity.
    :type quantity: str
    :param ordered: The updated order count.
    :type ordered: str

    """

    # Pull post parameters
    toner_id = request.POST["toner_id"]
    quantity = request.POST.get("quantity", None)
    ordered = request.POST.get("ordered", None)

    toner_instance = Toner.objects.get(id=toner_id)
    if quantity:
        toner_instance.quantity = int(quantity)
    if ordered:
        toner_instance.ordered = int(ordered)
    toner_instance.save()


@ajax
@require_POST
def update_part_inventory(request):
    """ Updates the inventory quantity of a printer part.

    :param part_id: The id of the toner cartridge to process.
    :type part_id: str
    :param quantity: The updated quantity.
    :type quantity: str
    :param ordered: The updated order count.
    :type ordered: str

    """

    # Pull post parameters
    part_id = request.POST["part_id"]
    quantity = request.POST.get("quantity", None)
    ordered = request.POST.get("ordered", None)

    part_instance = Part.objects.get(id=part_id)
    if quantity:
        part_instance.quantity = int(quantity)
    if ordered:
        part_instance.ordered = int(ordered)
    part_instance.save()
