"""
.. module:: resnet_internal.apps.network.views
   :synopsis: University Housing Internal Network Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from clever_selects.views import ChainedSelectFormViewMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.template import loader, Context
from django_datatables_view.mixins import JSONResponseView

from ..datatables.views import DatatablesView
from .airwaves.data import DeviceInfo, OverallBandwidthReport, DeviceBandwidthReport, OverallClientReport, ClientBandwidthReport, ClientInfo
from .ajax import PopulatePorts, PopulateAccessPoints, PopulateNetworkInfrastructureDevices
from .clearpass.utils import get_user_devices_info
from .clearpass.configuration import Endpoint
from .forms import PortCreateForm, AccessPointCreateForm, NetworkInfrastructureDeviceCreateForm
from .models import Port, AccessPoint, NetworkInfrastructureDevice
from .utils import validate_mac
from uh_internal.apps.network.models import ClearPassLoginAttempt
from uh_internal.apps.network.utils import mac_address_no_separator,\
    mac_address_with_colons


class PortsView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "network/ports.djhtml"
    form_class = PortCreateForm
    populate_class = PopulatePorts
    model = Port
    success_url = reverse_lazy('network:ports')


class AccessPointsView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "datatables/datatables_base.djhtml"
    form_class = AccessPointCreateForm
    populate_class = PopulateAccessPoints
    model = AccessPoint
    success_url = reverse_lazy('network:access_points')


class NetworkInfrastructureDevicesView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "datatables/datatables_base.djhtml"
    form_class = NetworkInfrastructureDeviceCreateForm
    populate_class = PopulateNetworkInfrastructureDevices
    model = NetworkInfrastructureDevice
    success_url = reverse_lazy('network:network_infrastructure_devices')


class AccessPointFrameView(DetailView):
    template_name = "network/ap_popover.djhtml"
    model = AccessPoint
    context_object_name = 'ap'


class PortFrameView(DetailView):
    template_name = "network/port_popover.djhtml"
    model = Port
    context_object_name = 'port'


class DeviceStatusView(TemplateView):
    template_name = "network/airwaves_device_status.djhtml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ap'] = DeviceInfo(kwargs['id'], extra_client_detail=True)

        return context


class DeviceBandwidthReportView(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = {}
        report = DeviceBandwidthReport(kwargs['id'], kwargs['device_type'])
        context['data'] = report.data

        return context


class ClientBandwidthReportView(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = {}
        report = ClientBandwidthReport(kwargs['mac_address'])
        context['data'] = report.data

        return context


class OverallBandwidthReportView(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = {}
        report = OverallBandwidthReport()
        context['data'] = report.data

        return context


class OverallClientReportView(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = {}
        report = OverallClientReport()
        context['data'] = report.data

        return context


class LoginAttemptInfoFrameView(DetailView):
    template_name = "network/login_attempt_popover.djhtml"
    model = ClearPassLoginAttempt
    context_object_name = 'login_attempt'


class TroubleshooterView(TemplateView):
    template_name = "network/troubleshooter.djhtml"


class TroubleshooterReportView(JSONResponseView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_query = self.request.POST['user_query'].strip()

        devices = {}

        if validate_mac(user_query):
            user_device = {
                'clearpass': Endpoint(user_query),
                'airwaves': ClientInfo(user_query),
                'login_attempts': ClearPassLoginAttempt.objects.filter(mac_address=mac_address_no_separator(user_query)),
            }

            devices[user_query] = user_device
        else:
            email_address = user_query if '@' in user_query else user_query + '@calpoly.edu'
            devices = get_user_devices_info(email_address)

        context['user_query'] = user_query
        context['device_list'] = []

        device_template = loader.get_template('network/troubleshooter_device_report.djhtml')

        for mac_address, device_info in devices:
            device = {
                'mac_address': mac_address_with_colons(mac_address),
                'type': device_info['clearpass'].profile['family'],
                'report': device_template.render(Context({'device': device_info})),
            }

            context['device_list'].append(device)

        return context
