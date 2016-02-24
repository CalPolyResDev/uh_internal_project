"""
.. module:: resnet_internal.apps.printers.ajax
   :synopsis: University Housing Internal Printer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict
from datetime import datetime
import shlex

from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse_lazy
from django.db.models.query_utils import Q

from ...settings.base import printers_modify_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView, BaseDatatablesRemoveView, RNINDatatablesFormView
from .forms import PrinterForm
from .models import Printer


OLD_YEARS = 3
OLDER_YEARS = 4
REPLACE_YEARS = 5


class PopulatePrinters(RNINDatatablesPopulateView):
    """Renders the printer index."""

    table_name = "printer_index"

    data_source = reverse_lazy('populate_printers')
    update_source = reverse_lazy('update_printer')
    form_source = reverse_lazy('form_printer')

    form_class = PrinterForm
    model = Printer

    item_name = 'printer'
    remove_url_name = 'remove_printer'

    column_definitions = OrderedDict()
    column_definitions["department"] = {"width": "200px", "type": "string", "title": "Department", "related": True, "lookup_field": "name"}
    column_definitions["sub_department"] = {"width": "200px", "type": "string", "title": "Sub Department", "related": True, "lookup_field": "name"}
    column_definitions["display_name"] = {"width": "200px", "type": "string", "title": "Printer Name"}
    column_definitions["mac_address"] = {"width": "150px", "type": "string", "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "string", "title": "IP Address"}
    column_definitions["model"] = {"width": "200px", "type": "string", "title": "Model"}
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
        self.write_permissions = printers_modify_access_test(user)

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
            return display_value if display_value else "DHCP"
        else:
            return super(PopulatePrinters, self).get_display_block(row, column)

    def filter_queryset(self, qs):
        search_parameters = self.request.GET.get('search[value]', None)
        searchable_columns = self.get_searchable_columns()
        flags = ["?dhcp", "?old", "?older", "?replace"]

        if search_parameters:
            try:
                params = shlex.split(search_parameters)
            except ValueError:
                params = search_parameters.split(" ")
            columnQ = Q()
            paramQ = Q()

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

            for param in params:
                if param != "" and param not in flags:
                    for searchable_column in searchable_columns:
                        columnQ |= Q(**{searchable_column + "__icontains": param})

                    paramQ.add(columnQ, Q.AND)
                    columnQ = Q()
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class RetrievePrinterForm(RNINDatatablesFormView):
    populate_class = PopulatePrinters


class UpdatePrinter(BaseDatatablesUpdateView):
    form_class = PrinterForm
    model = Printer
    populate_class = PopulatePrinters


class RemovePrinter(BaseDatatablesRemoveView):
    model = Printer
