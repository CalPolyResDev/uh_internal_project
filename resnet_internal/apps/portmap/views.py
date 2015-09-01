"""
.. module:: resnet_internal.apps.portmap.views
   :synopsis: ResNet Internal Residence Halls Port Map Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from django.core.urlresolvers import reverse_lazy

from ..datatables.views import DatatablesView
from .ajax import PopulateResidenceHallWiredPorts
from .forms import ResHallWiredPortCreateForm
from .models import ResHallWired


class ResidenceHallWiredPortsView(DatatablesView):
    template_name = "portmap/portmap.html"
    form_class = ResHallWiredPortCreateForm
    populate_class = PopulateResidenceHallWiredPorts
    model = ResHallWired
    success_url = reverse_lazy('residence_halls_wired_ports')
