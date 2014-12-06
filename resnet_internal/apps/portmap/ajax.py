"""
.. module:: resnet_internal.apps.portmap.ajax
   :synopsis: ResNet Internal Residence Halls Port Map AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging
from collections import OrderedDict

from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.contrib.staticfiles.templatetags.staticfiles import static

from django_ajax.decorators import ajax
from rmsconnector.utils import Resident

from ...settings.base import portmap_modify_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView, redraw_row
from .models import ResHallWired
from .forms import ResHallWiredPortUpdateForm

logger = logging.getLogger(__name__)


class PopulateResidenceHallWiredPorts(RNINDatatablesPopulateView):
    """Renders the port map."""

    table_name = "residence_halls_wired_port_map"
    data_source = reverse_lazy('populate_residence_halls_wired_ports')
    update_source = reverse_lazy('update_residence_halls_wired_port')
    model = ResHallWired
    max_display_length = 1000

    column_definitions = OrderedDict()
    column_definitions["id"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "ID"}
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": False, "title": "Community"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": False, "title": "Building"}
    column_definitions["room"] = {"width": "50px", "type": "string", "editable": False, "title": "Room"}
    column_definitions["switch_ip"] = {"width": "150px", "type": "ip-address", "title": "Switch IP"}
    column_definitions["switch_name"] = {"width": "100px", "type": "string", "title": "Switch Name"}
    column_definitions["jack"] = {"width": "50px", "type": "string", "editable": False, "title": "Jack"}
    column_definitions["blade"] = {"width": "50px", "type": "numeric", "title": "Blade"}
    column_definitions["port"] = {"width": "50px", "type": "numeric", "title": "Port"}
    column_definitions["vlan"] = {"width": "55px", "type": "string", "className": "edit_trigger", "title": "vLan"}
    column_definitions["active"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "lengthMenu": 'Display <select>'+
                '<option value="50">50</option>'+
                '<option value="100">100</option>'+
                '<option value="250">250</option>'+
                '<option value="500">500</option>'+
                '<option value="1000">1000</option>'+
                '<option value="-1">All</option>'+
                '</select> records:',
            "search": "Filter records: (Use ?pinhole and/or ?domain to narrow results.)",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["active"] = {"width": "50px", "type": "string", "editable": False, "title": "&nbsp;"}

        return super(PopulateResidenceHallWiredPorts, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = portmap_modify_access_test(user)

    def render_column(self, row, column):
        if column == 'switch_ip':
            value = getattr(row, column)

            ip_url = "/external/cisco/{ip_address}/".format(ip_address=value)

            editable_block = self.editable_block_template.format(value=value)
            link_block = self.link_block_template.format(link_url=ip_url, onclick_action="", link_target="_blank", link_class_name="", link_style="", link_text=value)
            inline_images = self.icon_template.format(icon_url=static('images/icons/cisco.gif'))

            return self.base_column_template.format(id=row.id, class_name="editable" if getattr(row, 'active') else "disabled",
                                                    column=column, value="", link_block=link_block, inline_images=inline_images, editable_block=editable_block)
        elif column == 'active':
            onclick = "confirm_status_change({id});return false;".format(id=row.id)
            link_block = self.link_block_template.format(link_url="", onclick_action=onclick, link_target="", link_class_name="", link_style="color:red; cursor:pointer;", link_text="Deactivate" if getattr(row, column) else "Activate")

            return self.base_column_template.format(id=row.id, class_name="" if getattr(row, column) else "disabled", column=column, value="", link_block=link_block, inline_images="", editable_block="")
        elif column in self.get_editable_columns() and self.get_write_permissions():
            value = getattr(row, column)
            editable_block = self.editable_block_template.format(value=value)
            return self.base_column_template.format(id=row.id, class_name="editable" if getattr(row, 'active') else "disabled", column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
        else:
            return self.base_column_template.format(id=row.id, class_name="" if getattr(row, 'active') else "disabled", column=column, value=getattr(row, column), link_block="", inline_images="", editable_block="")

    def filter_queryset(self, qs):
        search_parameters = self.request.GET.get('search[value]', None)
        searchable_columns = self.get_searchable_columns()

        if search_parameters:
            params = search_parameters.split(" ")
            columnQ = Q()
            paramQ = Q()

            # Check for pinhole / domain flags
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
                    for searchable_column in searchable_columns:
                        columnQ |= Q(**{searchable_column + "__icontains": param})

                    paramQ.add(columnQ, Q.AND)
                    columnQ = Q()
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class UpdateResidenceHallWiredPort(BaseDatatablesUpdateView):
    form_class = ResHallWiredPortUpdateForm
    model = ResHallWired
    populate_class = PopulateResidenceHallWiredPorts


@ajax
def change_port_status(request):
    """ Activates or Deactivates a port in the portmap.

    :param port_id: The port's id.
    :type port_id: int

    """

    # Pull post parameters
    port_id = request.POST["port_id"]

    port_instance = ResHallWired.objects.get(id=port_id)
    if port_instance.active:
        port_instance.active = False
    else:
        port_instance.active = True
    port_instance.save()

    return redraw_row(request, PopulateResidenceHallWiredPorts, port_id)
