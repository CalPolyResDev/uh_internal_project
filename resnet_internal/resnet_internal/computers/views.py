"""
.. module:: resnet_internal.computers.views
   :synopsis: ResNet Internal Computer Index Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings
from django.db.models import Q
from django.views.generic.base import TemplateView

from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import Computer, Pinhole, DNSRecord, DomainName


class ComputersView(BaseDatatableView):
    """Renders the computer index."""

    model = Computer

    # define the columns that will be returned
    columns = ['id', 'department', 'sub_department', 'computer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description']

    # define column names that can be sorted?
    order_columns = columns

    # define columns that can be searched
    searchable_columns = ['department', 'sub_department', 'computer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description']

    # define columns that can be edited
    editable_columns = ['department', 'sub_department', 'computer_name', 'ip_address', 'property_id', 'dn', 'description']

    def render_column(self, row, column):
        """Render columns with customized HTML.

        :param row: A dictionary containing row data.
        :type row: dict
        :param column: The name of the column to be rendered. This can be used to index into the row dictionary.
        :type column: str
        :returns: The HTML to be displayed for this column.

        """

        if column == 'ip_address':
            return "<div id='%s' class='editable' column='%s'><div class='display_data'><a href='/computers/%s/' class='iprecord'>%s</a><img src='%simages/icons/ip_record.png' style='padding-left:5px;' align='top' width='16' height='16' border='0' /></div><input type='text' class='editbox' value='%s' /></div>" % (row.id, column, getattr(row, column), getattr(row, column), settings.STATIC_URL, getattr(row, column))
        elif column in self.editable_columns:
            return "<div id='%s' class='editable' column='%s'><span class='display_data'>%s</span><input type='text' class='editbox' value='%s' /></div>" % (row.id, column, getattr(row, column), getattr(row, column))
        else:
            return "<div id='%s' column='%s'>%s</div>" % (row.id, column, getattr(row, column))

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
            qs = qs.filter(paramQ)

        return qs


class ComputerRecordsView(TemplateView):
    template_name = "computers/computer_record.html"

    def get_context_data(self, **kwargs):
        context = super(ComputerRecordsView, self).get_context_data(**kwargs)

        ip_address = context['ip_address']

        pinholes = Pinhole.objects.filter(ip_address=ip_address)
        dns_records = DNSRecord.objects.filter(ip_address=ip_address)
        domain_names = DomainName.objects.filter(ip_address=ip_address)

        context['pinholes'] = pinholes
        context['dns_records'] = dns_records
        context['domain_names'] = domain_names

        return context
