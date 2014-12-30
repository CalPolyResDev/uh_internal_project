"""
.. module:: resnet_internal.apps.portmap.ajax
   :synopsis: ResNet Internal Residence Halls Port Map AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging
import time
import socket
from collections import OrderedDict

from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.decorators.http import require_POST
from django.conf import settings

from django_ajax.decorators import ajax
from rmsconnector.utils import Resident

import paramiko

from ...settings.base import portmap_modify_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView, redraw_row
from .models import ResHallWired
from .forms import ResHallWiredPortUpdateForm
from paramiko.ssh_exception import SSHException

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
@require_POST
def change_port_status(request):
    """ Activates or Deactivates a port in the portmap.

    :param port_id: The port's id.
    :type port_id: int

    """

    # ALEX: I am putting try/except statements that simply print the general error
    #       message for the given error, so if you want to setup actual logging and
    #       anything else I missed then feel free. I was just unsure of what needed
    #       to get done to set that all up.
    #       It is possible to obtain the output from the server and then parse that to
    #       tell if the command worked as intended which I can implement with some
    #       more time. 

    # Pull post parameters
    port_id = request.POST["port_id"]

    port_instance = ResHallWired.objects.get(id=port_id)

    print ('switch_ip:', port_instance.switch_ip)
    print ('port:', port_instance.port)
    print ('blade:', port_instance.blade)

    # Set up paramiko ssh client
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(str(port_instance.switch_ip), username='resnetapi', password='PASSWORD GOES HERE', allow_agent=False, look_for_keys=False)
    except paramiko.AuthenticationException:
        print ('Error authenticating with the server')
    except (paramiko.SSHException, socket.error):
        print ('Error connecting to server')

    # Set up paramiko ssh shell (needed to send multiple commands before client closes itself
    try:
        ssh_shell = ssh_client.invoke_shell()
    except paramiko.SSHException:
        print ('Error connecting to server')

    if ssh_shell.get_transport().is_active():
        ssh_shell.send('conf t\n')
        time.sleep(.5)
        ssh_shell.send('interface Gi' + str(port_instance.blade) + '/' + str(port_instance.port) + '\n')
        time.sleep(.5)
    else:
        print ('Error: connection to server lost')

    if ssh_shell.get_transport().is_active():
        if port_instance.active:
            ssh_shell.send('shutdown\n')
            time.sleep(.5)
            port_instance.active = False
        else:
            ssh_shell.send('no shutdown\n')
            time.sleep(.5)
            port_instance.active = True
    else:
        print ('Error: connection to server lost')
    port_instance.save()

    # Close ssh connection(s)
    ssh_shell.close()
    ssh_client.close()

    return redraw_row(request, PopulateResidenceHallWiredPorts, port_id)
