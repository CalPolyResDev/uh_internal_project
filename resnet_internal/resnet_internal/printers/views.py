"""
.. module:: reslife_internal.printers.views
   :synopsis: ResLife Internal Printer Request Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.core.urlresolvers import reverse_lazy
from django.db.models import Q

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

from resnet_internal.settings.base import portmap_modify_access_test
from .forms import NewPrinterForm, TonerCountForm, PartCountForm
from .models import Printer, Request, Toner, Part

logger = logging.getLogger(__name__)


class PrintersView(CreateView):
    template_name = "printers/printers.html"
    form_class = NewPrinterForm
    model = Printer
    fields = NewPrinterForm.Meta.fields
    success_url = reverse_lazy('uh_printers')


class PopulatePrinters(BaseDatatableView):
    """Renders the printer index."""

    model = Printer
    max_display_length = 250

    # define the columns that will be returned
    columns = ['id', 'department', 'sub_department', 'printer_name', 'mac_address', 'ip_address', 'model', 'serial_number', 'property_id', 'dn', 'description', 'remove']

    # define column names that can be sorted?
    order_columns = columns

    # define columns that can be searched
    searchable_columns = ['department', 'sub_department', 'printer_name', 'mac_address', 'ip_address', 'model', 'serial_number', 'property_id', 'dn', 'description']

    # define columns that can be edited
    editable_columns = ['department', 'sub_department', 'printer_name', 'ip_address', 'property_id', 'dn', 'description']

    def render_column(self, row, column):
        """Render columns with customized HTML.

        :param row: A dictionary containing row data.
        :type row: dict
        :param column: The name of the column to be rendered. This can be used to index into the row dictionary.
        :type column: str
        :returns: The HTML to be displayed for this column.

        """

        if column == 'remove':
            return """<div id='{id}' column='{column}'><a style="color:red; cursor:pointer;" onclick="confirm_remove({id});">Remove</a></div>""".format(id=row.id, column=column)
        elif column in self.editable_columns and portmap_modify_access_test(self.request.user):
            return """<div id='{id}' class='editable' column='{column}'>
                       <span class='display_data'>{value}</span>
                       <input type='text' class='editbox' value='{value}' /></div>""".format(id=row.id, column=column, value=getattr(row, column))
        else:
            return """<div id='{id}' column='{column}'>{value}</div>""".format(id=row.id, column=column, value=getattr(row, column))

    def filter_queryset(self, qs):
        """ Filters the QuerySet by submitted search parameters.

        Made to work with multiple word search queries.
        PHP source: http://datatables.net/forums/discussion/3343/server-side-processing-and-regex-search-filter/p1
        Credit for finding the Q.AND method: http://bradmontgomery.blogspot.com/2009/06/adding-q-objects-in-django.html

        :param qs: The QuerySet to be filtered.
        :type qs: QuerySet
        :returns: If search parameters exist, the filtered QuerySet, otherwise the original QuerySet.

        """

        search_parameters = self.request.GET.get('sSearch', None)

        if search_parameters:
            params = search_parameters.split(" ")
            columnQ = None
            paramQ = None
            firstCol = True
            firstParam = True

            for param in params:
                if param != "":
                    for searchable_column in self.searchable_columns:
                        kwargz = {searchable_column + "__icontains": param}
                        q = Q(**kwargz)
                        if (firstCol):
                            firstCol = False
                            columnQ = q
                        else:
                            columnQ |= q
                    if (firstParam):
                        firstParam = False
                        paramQ = columnQ
                    else:
                        paramQ.add(columnQ, Q.AND)
                    columnQ = None
                    firstCol = True
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class RequestsListView(ListView):
    """Lists all open printer requests and supplies a form to modify the request status."""

    template_name = "printers/viewrequests.html"

    def get_queryset(self):
        return Request.objects.exclude(status=Request.STATUSES.index('Delivered'))


class InventoryView(TemplateView):
    """Lists inventory for both parts and toner."""

    template_name = "printers/viewinventory.html"
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

    template_name = "printers/viewordered.html"
