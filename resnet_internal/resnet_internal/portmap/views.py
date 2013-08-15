"""
.. module:: resnet_internal.portmap.views
   :synopsis: ResNet Internal Residence Halls Port Map Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.db.models import Q

from rmsconnector.utils import Resident
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import ResHallWired


class ModifyPort(View):
    """Updates modified port map data."""

    def post(self, *args, **kwargs):
        # Update the database entries
        portmap_instance = ResHallWired.objects.get(id=self.request.POST['id'])

        for column in ResidenceHallWiredPortsView.editable_columns:
            portmap_instance.column = self.request.POST[column]

        portmap_instance.save()


class ResidenceHallWiredPortsView(BaseDatatableView):
    """Renders the port map."""

    model = ResHallWired

    # define the columns that will be returned
    columns = ['id', 'community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan']

    # define column names that can be sorted
    order_columns = columns

    # define columns that can be searched
    searchable_columns = ['community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan']

    # define columns that can be edited
    editable_columns = ['switch_ip', 'switch_name', 'blade', 'port', 'vlan']

    def render_column(self, row, column):
        """Render columns with customized HTML.

        :param row: A dictionary containing row data.
        :type row: dict
        :param column: The name of the column to be rendered. This can be used to index into the row dictionary.
        :type column: str
        :returns: The HTML to be displayed for this column.

        """

        if column == 'switch_ip':
            return "<div id='%s' class='editable' column='%s'><div class='display_data'><a href='/frame/cisco/%s/' target='_blank'>%s</a><img src='%simages/icons/cisco.gif' style='padding-left:5px;' align='top' width='16' height='16' border='0' /></div><input type='text' class='editbox' value='%s' /></div>" % (row.id, column, getattr(row, column), getattr(row, column), settings.STATIC_URL, getattr(row, column))
        elif column in self.editable_columns:
            return "<div id='%s' class='editable' column='%s'><span class='display_data'>%s</span><input type='text' class='editbox' value='%s' /></div>" % (row.id, column, getattr(row, column), getattr(row, column))
        else:
            return "<div id='%s' column='%s'>%s</div>" % (row.id, column, getattr(row, column))

    def filter_queryset(self, qs):
        """ Filters the QuerySet by submitted search parameters.

        Made to work with multiple word search queries and an optional lookup flag.
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

            # Check for RMS Lookup Flag
            for param in params:
                if param[:1] == '?':
                    alias = param[1:]

                    if alias != "":
                        try:
                            resident = Resident(alias=alias)
                            lookup = resident.get_address()
                            params = [lookup['community'], lookup['building'], lookup['room']]
                        except (ObjectDoesNotExist, ImproperlyConfigured):
                            params = ['Address', 'Not', 'Found']
                    break

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
