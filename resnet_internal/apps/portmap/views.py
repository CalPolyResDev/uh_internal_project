"""
.. module:: resnet_internal.apps.portmap.views
   :synopsis: ResNet Internal Residence Halls Port Map Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView

from resnet_internal.apps.portmap.forms import AccessPointCreateForm

from ..datatables.views import DatatablesView
from .ajax import PopulateResidenceHallWiredPorts, PopulateResidenceHallAccessPoints
from .forms import ResHallWiredPortCreateForm
from .models import ResHallWired, AccessPoint


class ResidenceHallWiredPortsView(DatatablesView):
    template_name = "portmap/portmap.html"
    form_class = ResHallWiredPortCreateForm
    populate_class = PopulateResidenceHallWiredPorts
    model = ResHallWired
    success_url = reverse_lazy('residence_halls_wired_ports')


class ResidenceHallAccessPointsView(DatatablesView):
    template_name = "portmap/apmap.html"
    form_class = AccessPointCreateForm
    populate_class = PopulateResidenceHallAccessPoints
    model = AccessPoint
    success_url = reverse_lazy('residence_halls_access_points')


class AccessPointFrameView(DetailView):
    template_name = "portmap/ap_popover.html"
    model = AccessPoint
    context_object_name = 'ap'
