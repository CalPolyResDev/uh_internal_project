"""
.. module:: resnet_internal.apps.core.views
   :synopsis: ResNet Internal Core Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import datetime

from django.core.urlresolvers import reverse_lazy
from django.template.context import RequestContext
from django.views.generic import TemplateView
from srsconnector.models import ServiceRequest

from clever_selects.views import ChainedSelectFormViewMixin

from ..datatables.views import DatatablesView
from .ajax import PopulateResidenceHallRooms
from .forms import RoomCreateForm
from .models import SiteAnnouncements, Room


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):

        context = super(TemplateView, self).get_context_data(**kwargs)
        context['announcements'] = SiteAnnouncements.objects.all().order_by('-created')[:3]

        return context


class TicketSummaryView(TemplateView):
    template_name = 'core/ticket_summary.html'

    def get_context_data(self, **kwargs):
        context = super(TicketSummaryView, self).get_context_data(**kwargs)
        ticket_id = kwargs['ticket_id']
        context['ticket'] = ServiceRequest.objects.get(ticket_id=ticket_id)

        time_difference = (datetime.today() - context['ticket'].date_updated).total_seconds() / 86400

        if time_difference < 3:
            context['date_display_class'] = 'text-success'
        elif time_difference < 7:
            context['date_display_class'] = 'text-info'
        elif time_difference < 14:
            context['date_display_class'] = 'text-warning'
        else:
            context['date_display_class'] = 'text-danger'

        return context


class ResidenceHallRoomsView(ChainedSelectFormViewMixin, DatatablesView):
    template_name = "core/rooms.html"
    form_class = RoomCreateForm
    populate_class = PopulateResidenceHallRooms
    model = Room
    success_url = reverse_lazy('residence_halls_rooms')


def handler500(request):
    """500 error handler which includes ``request`` in the context."""

    from django.template import loader
    from django.http import HttpResponseServerError

    template = loader.get_template('500.html')

    return HttpResponseServerError(template.render(RequestContext(request)))
