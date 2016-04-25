"""
.. module:: resnet_internal.apps.network.ajax
   :synopsis: University Housing Internal Network AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

from collections import OrderedDict
import logging
import time

from clever_selects.views import ChainedSelectChoicesView
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist, ValidationError
from django.template import Template, Context
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.encoding import smart_str
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax
from django_datatables_view.mixins import JSONResponseView
from paramiko import SSHClient, AutoAddPolicy
from rmsconnector.utils import Resident

from ...settings.base import NETWORK_MODIFY_ACCESS
from ..datatables.ajax import RNINDatatablesPopulateView, RNINDatatablesFormView, BaseDatatablesUpdateView, BaseDatatablesRemoveView, redraw_row
from .clearpass.configuration import Endpoint
from .clearpass.utils import get_device_login_attempts
from .forms import PortCreateForm, PortUpdateForm, AccessPointCreateForm, AccessPointUpdateForm, NetworkInfrastructureDeviceCreateForm, NetworkInfrastructureDeviceUpdateForm
from .models import Port, AccessPoint, NetworkInfrastructureDevice
from .utils import device_is_down, validate_mac


logger = logging.getLogger(__name__)


class PopulatePorts(RNINDatatablesPopulateView):
    """Renders the port map."""

    table_name = "ports"

    data_source = reverse_lazy('network:populate_ports')
    update_source = reverse_lazy('network:update_port')
    form_source = reverse_lazy('network:form_port')
    extra_related = ['downstream_devices']

    form_class = PortCreateForm
    model = Port

    item_name = 'port'
    remove_url_name = 'network:remove_port'

    column_definitions = OrderedDict()
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": False, "title": "Community", "custom_lookup": True, "lookup_field": "room__building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": False, "title": "Building", "custom_lookup": True, "lookup_field": "room__building__name"}
    column_definitions["room"] = {"width": "80px", "type": "string", "editable": False, "title": "Room", "related": True, "lookup_field": "name"}
    column_definitions["switch_name"] = {"width": "100px", "type": "string", "title": "Switch Name", "custom_lookup": True, "lookup_field": "upstream_device__display_name"}
    column_definitions["switch_ip"] = {"width": "150px", "type": "ip-address", "title": "Switch IP", "custom_lookup": True, "lookup_field": "upstream_device__ip_address"}
    column_definitions["display_name"] = {"width": "50px", "type": "string", "editable": False, "title": "Jack"}
    column_definitions["blade_number"] = {"width": "50px", "type": "numeric", "title": "Blade"}
    column_definitions["port_number"] = {"width": "50px", "type": "numeric", "title": "Port"}
    column_definitions["downstream_devices"] = {"width": "50px", "type": "html", "searchable": False, "orderable": False, "editable": False, "title": "AP", "related": True, "lookup_field": "id"}
    column_definitions["active"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "search": "Filter records: (?email)",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["active"].update({"width": "90px", "type": "string", "visible": True})
            self.column_definitions["remove"].update({"width": "70px", "type": "string", "remove_column": True, "visible": True})

        return super().get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = user.has_access(NETWORK_MODIFY_ACCESS)

    def get_row_class(self, row):
        if device_is_down(row.upstream_device):
            return 'danger'
        elif not row.active:
            return "disabled"
        else:
            return super().get_row_class(row)

    def render_column(self, row, column):
        if column == 'downstream_devices':
            try:
                access_point = row.downstream_devices.all()[0]
            except (ObjectDoesNotExist, IndexError):
                link_block = ""
            else:
                ap_url = reverse('network:access_point_info_frame', kwargs={'pk': access_point.id})
                ap_icon = self.icon_template.format(icon_url=static('images/icons/wifi-xxl.png'))
                link_block = self.popover_link_block_template.format(popover_title='AP Info', content_url=ap_url, link_class_name="", link_display=ap_icon)

            display_block = self.display_block_template.format(value="", link_block=link_block, inline_images="")
            return self.base_column_template.format(column=column, display_block=display_block, form_field_block="")
        elif column == 'active':
            if device_is_down(row.upstream_device):
                return self.display_block_template.format(value="", link_block="", inline_images="")
            else:
                return self.render_action_column(row=row, column=column, function_name="confirm_status_change", link_class_name="action_blue", link_display="Deactivate" if getattr(row, column) else "Activate")
        else:
            return super().render_column(row, column)

    def get_extra_params(self, params):
        # Check for email lookup flag
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

        return params


class RetrievePortForm(RNINDatatablesFormView):
    populate_class = PopulatePorts


class UpdatePort(BaseDatatablesUpdateView):
    form_class = PortUpdateForm
    model = Port
    populate_class = PopulatePorts


class RemovePort(BaseDatatablesRemoveView):
    model = Port


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
    ssh_client.connect(str(port_instance.upstream_device.ip_address), username=settings.RESNET_SWITCH_SSH_USER, password=settings.RESNET_SWITCH_SSH_PASSWORD, allow_agent=False, look_for_keys=False)
    ssh_shell = ssh_client.invoke_shell()

    if ssh_shell.get_transport().is_active():
        ssh_shell.send('conf t\n')
        time.sleep(.5)
        ssh_shell.send('interface Gi' + str(port_instance.blade_number) + '/' + str(port_instance.port_number) + '\n')
        time.sleep(.5)
    else:
        raise IOError('Lost connection to switch {switch}.'.format(switch=port_instance.upstream_device.ip_address))

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
        raise IOError('Lost connection to switch {switch}.'.format(switch=port_instance.upstream_device.ip_address))

    # Close ssh connection(s)
    ssh_shell.close()
    ssh_client.close()

    return redraw_row(request, PopulatePorts, port_id)


class PopulateAccessPoints(RNINDatatablesPopulateView):
    """Renders the access point map."""

    table_name = "access_point_map"

    data_source = reverse_lazy('network:populate_access_points')
    update_source = reverse_lazy('network:update_access_point')
    form_source = reverse_lazy('network:form_access_point')

    form_class = AccessPointCreateForm
    model = AccessPoint

    item_name = 'access point'
    remove_url_name = 'network:remove_access_point'

    extra_options = {
        "language": {
            "search": "Filter records: (?email)",
        },
    }

    extra_related = [
        'upstream_device__port',
        'upstream_device__upstream_device',
    ]

    column_definitions = OrderedDict()
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": False, "title": "Community", "custom_lookup": True, "lookup_field": "room__building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": False, "title": "Building", "custom_lookup": True, "lookup_field": "room__building__name"}
    column_definitions["room"] = {"width": "80px", "type": "string", "editable": False, "title": "Room", "related": True, "lookup_field": "name"}
    column_definitions["upstream_device"] = {"width": "40px", "type": "string", "editable": False, "title": "Jack", "related": True, "lookup_field": "id"}
    column_definitions["dns_name"] = {"width": "80px", "type": "string", "title": "Name"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "title": "Serial Number"}
    column_definitions["mac_address"] = {"width": "125px", "type": "string", "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "string", "title": "IP Address"}
    column_definitions["ap_type"] = {"width": "80px", "type": "string", "title": "Type"}
    column_definitions["airwaves_id"] = {"width": "10px", "type": "string", "orderable": False}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"].update({"width": "80px", "type": "string", "remove_column": True, "visible": True})

        return super().get_options()

    def get_row_class(self, row):
        if device_is_down(row.upstream_device.upstream_device):
            return 'danger'
        else:
            return super().get_row_class(row)

    def _initialize_write_permissions(self, user):
        self.write_permissions = user.has_access(NETWORK_MODIFY_ACCESS)

    def get_display_block(self, row, column):
        if column == 'upstream_device':
            port = row.upstream_device.port
            port_url = reverse('network:port_info_frame', kwargs={'pk': port.id})
            port_icon = self.icon_template.format(icon_url=static('images/icons/icon_ethernet.png'))
            port_block = self.popover_link_block_template.format(popover_title='Port Info', content_url=port_url, link_class_name="", link_display=port_icon)
            return self.display_block_template.format(value=port.jack, link_block=port_block, inline_images="")
        elif column == 'airwaves_id':
            if row.airwaves_id:
                icon_block = self.icon_template.format(icon_url=static('images/icons/aruba.png'))
                device_status_url = reverse('network:airwaves_device_status', kwargs={'id': row.airwaves_id})
                onclick = """openModalFrame("AP Status: {name}", "{url}");""".format(name=row.display_name, url=device_status_url)
                link_block = self.onclick_link_block_template.format(onclick_action=onclick, link_class_name="", link_display=icon_block)
                return self.display_block_template.format(value='', link_block=link_block, inline_images='')
            else:
                return ''
        else:
            return super().get_display_block(row, column)

    def get_extra_params(self, params):
        # Check for email lookup flag
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

        return params


class RetrieveAccessPointForm(RNINDatatablesFormView):
    populate_class = PopulateAccessPoints


class UpdateAccessPoint(BaseDatatablesUpdateView):
    form_class = AccessPointUpdateForm
    model = AccessPoint
    populate_class = PopulateAccessPoints


class RemoveAccessPoint(BaseDatatablesRemoveView):
    model = AccessPoint


class PortChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Port.objects.filter(room__id=self.parent_value)


class PopulateNetworkInfrastructureDevices(RNINDatatablesPopulateView):
    table_name = 'network_infrastructure_device_map'

    data_source = reverse_lazy('network:populate_network_infrastructure_devices')
    update_source = reverse_lazy('network:update_network_infrastructure_device')
    form_source = reverse_lazy('network:form_network_infrastructure_device')

    form_class = NetworkInfrastructureDeviceCreateForm
    model = NetworkInfrastructureDevice

    item_name = 'network infrastructure device'
    remove_url_name = 'network:remove_network_infrastructure_device'

    column_definitions = OrderedDict()
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": True, "title": "Community", "custom_lookup": True, "lookup_field": "room__building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": True, "title": "Building", "custom_lookup": True, "lookup_field": "room__building__name"}
    column_definitions["room"] = {"width": "80px", "type": "string", "editable": True, "title": "Room", "related": True, "lookup_field": "name"}
    column_definitions["display_name"] = {"width": "80px", "type": "string", "title": "Name"}
    column_definitions["dns_name"] = {"width": "80px", "type": "string", "title": "DNS"}
    column_definitions["ip_address"] = {"width": "150px", "type": "string", "title": "IP Address"}
    column_definitions["airwaves_id"] = {"width": "10px", "type": "string", "title": "", "orderable": False}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"].update({"width": "80px", "type": "string", "remove_column": True, "visible": True})

        return super().get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = user.has_access(NETWORK_MODIFY_ACCESS)

    def get_display_block(self, row, column):
        if column == 'airwaves_id':
            if row.airwaves_id:
                icon_block = self.icon_template.format(icon_url=static('images/icons/aruba.png'))
                device_status_url = reverse('network:airwaves_device_status', kwargs={'id': row.airwaves_id})
                onclick = """openModalFrame("Network Infrastructure Device Status: {name}", "{url}");""".format(name=row.display_name, url=device_status_url)
                link_block = self.onclick_link_block_template.format(onclick_action=onclick, link_class_name="", link_display=icon_block)
                return self.display_block_template.format(value='', link_block=link_block, inline_images='')
            else:
                return ''
        else:
            return super().get_display_block(row, column)


class RetrieveNetworkInfrastructureDeviceForm(RNINDatatablesFormView):
    populate_class = PopulateNetworkInfrastructureDevices


class UpdateNetworkInfrastructureDevice(BaseDatatablesUpdateView):
    form_class = NetworkInfrastructureDeviceUpdateForm
    model = NetworkInfrastructureDevice
    populate_class = PopulateNetworkInfrastructureDevices


class RemoveNetworkInfrastructureDevice(BaseDatatablesRemoveView):
    model = NetworkInfrastructureDevice


class EndpointBaseUpdateView(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = {}

        try:
            self.endpoint = Endpoint(kwargs['mac_address'])
            self.perform_change(**kwargs)
            context['success'] = True
        except Exception as exc:
            logger.exception('Could not perform endpoint change')
            context['success'] = False
            context['error'] = str(exc)

        return context

    def perform_change(self, **kwargs):
        pass


class EndpointChangeToKnown(EndpointBaseUpdateView):

    def perform_change(self, **kwargs):
        self.endpoint.set_to_known()


class EndpointSetAsGamingDevice(EndpointBaseUpdateView):

    def perform_change(self, **kwargs):
        self.endpoint.set_as_gaming_device()


class EndpointSetAsGamingPC(EndpointBaseUpdateView):

    def perform_change(self, **kwargs):
        self.endpoint.set_as_gaming_pc()


class EndpointSetAsMediaDevice(EndpointBaseUpdateView):

    def perform_change(self, **kwargs):
        self.endpoint.set_as_media_device()


class EndpointRemoveAttribute(EndpointBaseUpdateView):

    def perform_change(self, **kwargs):
        self.endpoint.remove_attribute(kwargs['attribute'])


class RetrieveLoginAttempts(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = {}

        mac_address = kwargs['mac_address']

        if not validate_mac(mac_address):
            raise ValidationError('Bad MAC Address: ' + mac_address)

        login_attempts = get_device_login_attempts(mac_address).order_by('-time')

        template = """
        {% load network_tags %}
        {% for attempt in login_attempts %}
            {% login_attempt_tr attempt %}
        {% endfor %}
        """

        context['login_attempts_table_body'] = Template(template).render(Context({'login_attempts': login_attempts}))

        return context
