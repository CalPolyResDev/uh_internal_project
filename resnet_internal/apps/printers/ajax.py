"""
.. module:: resnet_internal.apps.printers.ajax
   :synopsis: ResNet Internal Printer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict

from django.core.urlresolvers import reverse_lazy
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax

from ...settings.base import printers_modify_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView
from .models import Printer
from .forms import PrinterUpdateForm


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
