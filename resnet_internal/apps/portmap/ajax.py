"""
.. module:: resnet_internal.apps.network.ajax
   :synopsis: University Housing Internal Network AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

from collections import OrderedDict
import logging
import shlex
import time

from clever_selects.views import ChainedSelectChoicesView
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.utils.encoding import smart_str
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax
from paramiko import SSHClient, AutoAddPolicy

from rmsconnector.utils import Resident

from ...settings.base import ports_modify_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView, redraw_row
from .forms import PortCreateForm, PortUpdateForm, AccessPointCreateForm, AccessPointUpdateForm
from .models import Port, AccessPoint


logger = logging.getLogger(__name__)


class PopulatePorts(RNINDatatablesPopulateView):
    """Renders the port map."""

    table_name = "ports"
    data_source = reverse_lazy('populate_ports')
    update_source = reverse_lazy('update_port')
    form_class = PortCreateForm
    model = Port

    column_definitions = OrderedDict()
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": False, "title": "Community", "custom_lookup": True, "lookup_field": "room__building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": False, "title": "Building", "custom_lookup": True, "lookup_field": "room__building__name"}
    column_definitions["room"] = {"width": "80px", "type": "string", "editable": False, "title": "Room", "related": True, "lookup_field": "name"}
    column_definitions["switch_ip"] = {"width": "150px", "type": "ip-address", "title": "Switch IP"}
    column_definitions["switch_name"] = {"width": "100px", "type": "string", "title": "Switch Name"}
    column_definitions["jack"] = {"width": "50px", "type": "string", "editable": False, "title": "Jack"}
    column_definitions["blade"] = {"width": "50px", "type": "numeric", "title": "Blade"}
    column_definitions["port"] = {"width": "50px", "type": "numeric", "title": "Port"}
    column_definitions["access_point"] = {"width": "50px", "type": "html", "searchable": False, "orderable": False, "editable": False, "title": "AP"}
    column_definitions["active"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "search": "Filter records: (?email)",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["active"] = {"width": "80px", "type": "string", "editable": False, "title": "&nbsp;"}

        return super(PopulatePorts, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = ports_modify_access_test(user)

    def get_row_class(self, row):
        if not row.active:
            return "disabled"

    def render_column(self, row, column):
        if column == 'access_point':
            try:
                access_point = row.access_point
            except ObjectDoesNotExist:
                link_block = ""
            else:
                ap_url = reverse('ap_info_frame', kwargs={'pk': access_point.id})
                ap_icon = self.icon_template.format(icon_url=static('images/icons/wifi-xxl.png'))
                link_block = self.popover_link_block_template.format(popover_title='AP Info', content_url=ap_url, link_class_name="", link_display=ap_icon)

            display_block = self.display_block_template.format(value="", link_block=link_block, inline_images="")
            return self.base_column_template.format(column=column, display_block=display_block, form_field_block="")
        elif column == 'active':
            return self.render_action_column(row=row, column=column, function_name="confirm_status_change", link_class_name="remove", link_display="Deactivate" if getattr(row, column) else "Activate")
        elif column == 'remove':
            return self.render_action_column(row=row, column=column, function_name="confirm_remove", link_class_name="remove", link_display="Remove")
        else:
            return super(PopulatePorts, self).render_column(row, column)

    def filter_queryset(self, qs):
        search_parameters = self.request.GET.get('search[value]', None)
        searchable_columns = self.get_searchable_columns()

        if search_parameters:
            try:
                params = shlex.split(search_parameters)
            except ValueError:
                params = search_parameters.split(" ")
            columnQ = Q()
            paramQ = Q()

            # Check for pinhole / domain flags
            for param in params:
                if param[:1] == '?':
                    email = param[1:]

                    if email:
                        try:
                            resident = Resident(principal_name=email)
                            params = [resident.address_dict['community'], resident.address_dict['building'], resident.address_dict['room']]
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


class UpdatePort(BaseDatatablesUpdateView):
    form_class = PortUpdateForm
    model = Port
    populate_class = PopulatePorts


@ajax
@require_POST
def change_port_status(request):
    """ Activates or Deactivates a port.

    :param port_id: The port's id.
    :type port_id: int

    """

    # Pull post parameters
    port_id = request.POST["port_id"]

    port_instance = Port.objects.get(id=port_id)

    # Set up paramiko ssh client
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(str(port_instance.switch_ip), username=settings.RESNET_SWITCH_SSH_USER, password=settings.RESNET_SWITCH_SSH_PASSWORD, allow_agent=False, look_for_keys=False)
    ssh_shell = ssh_client.invoke_shell()

    if ssh_shell.get_transport().is_active():
        ssh_shell.send('conf t\n')
        time.sleep(.5)
        ssh_shell.send('interface Gi' + str(port_instance.blade) + '/' + str(port_instance.port) + '\n')
        time.sleep(.5)
    else:
        raise IOError('Lost connection to switch {switch}.'.format(switch=port_instance.switch_ip))

    if ssh_shell.get_transport().is_active():
        if port_instance.active:
            ssh_shell.send('shutdown\n')
            time.sleep(.5)
        else:
            ssh_shell.send('no shutdown\n')
            time.sleep(.5)

        buffer_size = 1024
        stderr = ""

        # Pull stderr from the buffer
        while ssh_shell.recv_stderr_ready():
            stderr += smart_str(ssh_shell.recv_stderr(buffer_size))

        # Attempt to parse errors
        if stderr:
            raise IOError(stderr)
        else:
            # An error did not occur.
            port_instance.active = not port_instance.active
            port_instance.save()
    else:
        raise IOError('Lost connection to switch {switch}.'.format(switch=port_instance.switch_ip))

    # Close ssh connection(s)
    ssh_shell.close()
    ssh_client.close()

    return redraw_row(request, PopulatePorts, port_id)


@ajax
@require_POST
def remove_port(request):
    """ Removes a port.

    :param port_id: The port's id.
    :type port_id: str

    """

    # Pull post parameters
    port_id = request.POST["port_id"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["port_id"] = port_id

    port = Port.objects.get(id=port_id)
    port.delete()

    return context


class PopulateAccessPoints(RNINDatatablesPopulateView):
    """Renders the access point map."""

    table_name = "access_point_map"
    data_source = reverse_lazy('populate_access_points')
    update_source = reverse_lazy('update_access_point')
    form_class = AccessPointCreateForm
    model = AccessPoint

    column_definitions = OrderedDict()
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": False, "title": "Community", "custom_lookup": True, "lookup_field": "port__room__building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": False, "title": "Building", "custom_lookup": True, "lookup_field": "port__room__building__name"}
    column_definitions["room"] = {"width": "80px", "type": "string", "editable": False, "title": "Room", "custom_lookup": True, "lookup_field": "port__room__name"}
    column_definitions["port"] = {"width": "80px", "type": "string", "editable": False, "title": "Jack", "related": True, "lookup_field": "jack"}
    column_definitions["name"] = {"width": "80px", "type": "string", "title": "Name"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "title": "Serial Number"}
    column_definitions["mac_address"] = {"width": "150px", "type": "string", "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "string", "title": "IP Address"}
    column_definitions["ap_type"] = {"width": "80px", "type": "string", "title": "Type"}

    def _initialize_write_permissions(self, user):
        self.write_permissions = ports_modify_access_test(user)

    def get_display_block(self, row, column):
        if column == 'port':
            port = row.port
            port_url = reverse('port_info_frame', kwargs={'pk': port.id})
            port_icon = self.icon_template.format(icon_url=static('images/icons/icon_ethernet.png'))
            port_block = self.popover_link_block_template.format(popover_title='Port Info', content_url=port_url, link_class_name="", link_display=port_icon)
            return self.display_block_template.format(value=port.jack, link_block=port_block, inline_images="")
        else:
            return super(PopulateAccessPoints, self).get_display_block(row, column)


class UpdateAccessPoint(BaseDatatablesUpdateView):
    form_class = AccessPointUpdateForm
    model = AccessPoint
    populate_class = PopulateAccessPoints


class PortChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Port.objects.filter(room__id=self.parent_value)
