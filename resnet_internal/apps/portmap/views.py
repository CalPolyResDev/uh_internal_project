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
from django_datatables_view.mixins import JSONResponseView

from ..datatables.views import DatatablesView
from .airwaves.data import DeviceInfo, OverallBandwidthReport, DeviceBandwidthReport, OverallClientReport
from .ajax import PopulatePorts, PopulateAccessPoints, PopulateNetworkInfrastructureDevices
from .forms import PortCreateForm, AccessPointCreateForm, NetworkInfrastructureDeviceCreateForm
from .models import Port, AccessPoint, NetworkInfrastructureDevice


class PortsView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "portmap/ports.djhtml"
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
    template_name = "portmap/ap_popover.djhtml"
    model = AccessPoint
    context_object_name = 'ap'


class PortFrameView(DetailView):
    template_name = "portmap/port_popover.djhtml"
    model = Port
    context_object_name = 'port'


class DeviceStatusView(TemplateView):
    template_name = "portmap/airwaves_device_status.djhtml"

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
