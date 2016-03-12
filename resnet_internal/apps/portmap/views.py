"""
.. module:: resnet_internal.apps.network.views
   :synopsis: University Housing Internal Network Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from clever_selects.views import ChainedSelectFormViewMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView

from ..datatables.views import DatatablesView
from .ajax import PopulatePorts, PopulateAccessPoints, PopulateNetworkInfrastructureDevices
from .forms import PortCreateForm, AccessPointCreateForm, NetworkInfrastructureDeviceCreateForm
from .models import Port, AccessPoint, NetworkInfrastructureDevice
from .airwaves.data import DeviceInfo, APClientInfo
from django.views.generic.base import TemplateView


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
    template_name = "portmap/ap_popover.html"
    model = AccessPoint
    context_object_name = 'ap'


class PortFrameView(DetailView):
    template_name = "portmap/port_popover.html"
    model = Port
    context_object_name = 'port'


class AccessPointStatusView(TemplateView):
    template_name = "portmap/ap_status.djhtml"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)

        context['ap'] = DeviceInfo(kwargs['id'], extra_client_detail=True)

        return context
