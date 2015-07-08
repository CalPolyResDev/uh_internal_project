"""
.. module:: resnet_internal.apps.printers.ajax
   :synopsis: ResNet Internal Printer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import shlex
from collections import OrderedDict
from datetime import datetime

from django.core.urlresolvers import reverse_lazy
from django.db.models.query_utils import Q
from django.views.decorators.http import require_POST

from dateutil.relativedelta import relativedelta
from django_ajax.decorators import ajax

from ...settings.base import printers_modify_access_test
from ..core.models import Department
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView
from .models import Printer
from .forms import PrinterUpdateForm

OLD_YEARS = 3
OLDER_YEARS = 4
REPLACE_YEARS = 5


class PopulatePrinters(RNINDatatablesPopulateView):
    """Renders the printer index."""

    table_name = "printer_index"
    data_source = reverse_lazy('populate_uh_printers')
    update_source = reverse_lazy('update_uh_printer')
    model = Printer

    # NOTE Installed Types: ip-address, mac-address

    column_definitions = OrderedDict()
    column_definitions["id"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "ID"}
    column_definitions["department"] = {"width": "225px", "type": "string", "title": "Department", "related": True, "lookup_field": "name"}
    column_definitions["sub_department"] = {"width": "225px", "type": "string", "title": "Sub Department", "related": True, "lookup_field": "name"}
    column_definitions["printer_name"] = {"width": "150px", "type": "string", "title": "Printer Name"}
    column_definitions["mac_address"] = {"width": "150px", "type": "mac-address", "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "ip-address", "title": "IP Address"}
    column_definitions["model"] = {"width": "100px", "type": "string", "title": "Model"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "title": "Serial Number"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["location"] = {"width": "225px", "type": "string", "title": "Location"}
    column_definitions["date_purchased"] = {"width": "100px", "type": "string", "searchable": False, "title": "Date Purchased"}
    column_definitions["description"] = {"width": "225px", "type": "string", "className": "edit_trigger", "title": "Description"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "search": "Filter records: (Use ?dhcp and/or ?replace to narrow results.) ",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"] = {"width": "50px", "type": "string", "searchable": False, "orderable": False, "editable": False, "title": "&nbsp;"}

        return super(PopulatePrinters, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = printers_modify_access_test(user)

    def render_column(self, row, column, class_names=None):
        if not class_names:
            class_names = []

        # Add colors
        if row.date_purchased:
            old_delta = datetime.now() - relativedelta(years=OLD_YEARS)
            older_delta = datetime.now() - relativedelta(years=OLDER_YEARS)
            replace_delta = datetime.now() - relativedelta(years=REPLACE_YEARS)

            puchase_datetime = datetime.fromordinal(row.date_purchased.toordinal())

            if puchase_datetime <= replace_delta:
                class_names.append("replace")
            elif puchase_datetime <= older_delta and puchase_datetime > replace_delta:
                class_names.append("older")
            elif puchase_datetime <= old_delta and puchase_datetime > older_delta:
                class_names.append("old")

        if column == 'department':
            department_instance = getattr(row, column)
            department_id = department_instance.id
            value = department_instance.name

            editable_block = self.format_select_block(queryset=Department.objects.all(), value_field="id", text_field="name", value_match=department_id)
            class_names.append("editable")

            return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
        elif column == 'sub_department':
            department_instance = getattr(row, "department")
            sub_department_instance = getattr(row, column)
            valid_sub_departments = department_instance.sub_departments.all()

            # Check to make sure the current value is acceptable for the selected department.
            # If it isn't, set it to the first valid one
            if sub_department_instance not in valid_sub_departments:
                sub_department_instance.id = valid_sub_departments[0].id
                sub_department_instance.name = valid_sub_departments[0].name
                sub_department_instance.save()

            department_id = department_instance.id
            sub_department_id = sub_department_instance.id
            value = sub_department_instance.name

            editable_block = self.format_select_block(queryset=valid_sub_departments, value_field="id", text_field="name", value_match=sub_department_id)
            class_names.append("editable")

            return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
        elif column == 'ip_address':
            value = getattr(row, column)
            value = value if value else "DHCP"

            editable_block = self.editable_block_template.format(value=value if value != "DHCP" else "")
            class_names.append("editable")

            return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
        elif column == 'remove':
            onclick = "confirm_remove({id});return false;".format(id=row.id)
            link_block = self.link_block_template.format(link_url="", onclick_action=onclick, link_target="", link_class_name="", link_style="color:red; cursor:pointer;", link_text="Remove")

            return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value="", link_block=link_block, inline_images="", editable_block="")
        else:
            return super(PopulatePrinters, self).render_column(row, column, class_names)

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
