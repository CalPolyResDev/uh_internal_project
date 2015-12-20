"""
.. module:: resnet_internal.apps.portmap.views
   :synopsis: ResNet Internal Residence Halls Port Map Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from clever_selects.views import ChainedSelectFormViewMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView

from resnet_internal.apps.portmap.forms import AccessPointCreateForm

from ..datatables.views import DatatablesView
from .ajax import PopulatePorts, PopulateAccessPoints
from .forms import PortCreateForm
from .models import Port, AccessPoint


class PortsView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "portmap/portmap.html"
    form_class = PortCreateForm
    populate_class = PopulatePorts
    model = Port
    success_url = reverse_lazy('residence_halls_wired_ports')


class AccessPointsView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "portmap/apmap.html"
    form_class = AccessPointCreateForm
    populate_class = PopulateAccessPoints
    model = AccessPoint
    success_url = reverse_lazy('residence_halls_access_points')


class AccessPointFrameView(DetailView):
    template_name = "portmap/ap_popover.html"
    model = AccessPoint
    context_object_name = 'ap'


class PortFrameView(DetailView):
    template_name = "portmap/port_popover.html"
    model = Port
    context_object_name = 'port'
