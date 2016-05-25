"""
.. module:: resnet_internal.apps.printers.ajax
   :synopsis: University Housing Internal Printer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse_lazy

from ...settings.base import PRINTERS_MODIFY_ACCESS
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView, BaseDatatablesRemoveView, RNINDatatablesFormView
from .forms import PrinterForm
from .models import Printer


OLD_YEARS = 3
OLDER_YEARS = 4
REPLACE_YEARS = 5


class PopulatePrinters(RNINDatatablesPopulateView):
    """Renders the printer index."""

    table_name = "printer_index"

    data_source = reverse_lazy('printers:populate')
    update_source = reverse_lazy('printers:update')
    form_source = reverse_lazy('printers:form')

    form_class = PrinterForm
    model = Printer

    item_name = 'printer'
    remove_url_name = 'printers:remove'

    column_definitions = OrderedDict()
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": True, "title": "Community", "custom_lookup": True, "lookup_field": "room__building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": True, "title": "Building", "custom_lookup": True, "lookup_field": "room__building__name"}
    column_definitions["room"] = {"width": "80px", "type": "string", "editable": True, "title": "Room", "related": True, "lookup_field": "name"}
    column_definitions["display_name"] = {"width": "200px", "type": "string", "title": "Printer Name"}
    column_definitions["mac_address"] = {"width": "150px", "type": "string", "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "string", "title": "IP Address"}
    column_definitions["model"] = {"width": "200px", "type": "string", "title": "Model"}
    column_definitions["department"] = {"width": "200px", "type": "string", "title": "Department", "related": True, "lookup_field": "name"}
    column_definitions["sub_department"] = {"width": "200px", "type": "string", "title": "Sub Department", "related": True, "lookup_field": "name"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "title": "Serial Number"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["location"] = {"width": "150px", "type": "string", "title": "Location"}
    column_definitions["date_purchased"] = {"width": "100px", "type": "string", "searchable": False, "title": "Date Purchased"}
    column_definitions["description"] = {"width": "250px", "type": "string", "title": "Description"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "search": "Filter records: (?dhcp, ?replace) ",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"].update({"width": "80px", "type": "string", "remove_column": True, "visible": True})

        return super(PopulatePrinters, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = user.has_access(PRINTERS_MODIFY_ACCESS)

    def get_row_class(self, row):
        if row.date_purchased:
            old_delta = datetime.now() - relativedelta(years=OLD_YEARS)
            older_delta = datetime.now() - relativedelta(years=OLDER_YEARS)
            replace_delta = datetime.now() - relativedelta(years=REPLACE_YEARS)

            puchase_datetime = datetime.fromordinal(row.date_purchased.toordinal())

            if puchase_datetime <= replace_delta:
                return "replace"
            elif puchase_datetime <= older_delta and puchase_datetime > replace_delta:
                return "older"
            elif puchase_datetime <= old_delta and puchase_datetime > older_delta:
                return "old"

    def get_display_block(self, row, column):
        if column == 'ip_address':
            display_value = self.get_raw_value(row, column)

            if not display_value:
                display_value = "DHCP"

            return self.display_block_template.format(value=display_value, link_block="", inline_images="")
        else:
            return super(PopulatePrinters, self).get_display_block(row, column)

    def check_params_for_flags(self, params, qs):
        flags = ["?dhcp", "?old", "?older", "?replace"]

        # Check for flags
        for param in params:
            if param[:1] == '?':
                flag = param[1:]

                if flag == "dhcp":
                    qs = qs.filter(dhcp=True)
                elif flag == "old":
                    qs = qs.filter(date_purchased__lte=datetime.now() - relativedelta(years=OLD_YEARS))
                elif flag == "older":
                    qs = qs.filter(date_purchased__lte=datetime.now() - relativedelta(years=OLDER_YEARS))
                elif flag == "replace":
                    qs = qs.filter(date_purchased__lte=datetime.now() - relativedelta(years=REPLACE_YEARS))

        return qs, flags


class RetrievePrinterForm(RNINDatatablesFormView):
    populate_class = PopulatePrinters


class UpdatePrinter(BaseDatatablesUpdateView):
    form_class = PrinterForm
    model = Printer
    populate_class = PopulatePrinters


class RemovePrinter(BaseDatatablesRemoveView):
    model = Printer
