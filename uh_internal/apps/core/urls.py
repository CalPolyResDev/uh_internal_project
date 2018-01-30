"""
.. module:: resnet_internal.apps.core.urls
   :synopsis: University Housing Internal Core URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView
from django_cas_ng.views import login as auth_login, logout as auth_logout
from django_js_reverse.views import urls_js

from .ajax import (BuildingChainedAjaxView, RoomChainedAjaxView, SubDepartmentChainedAjaxView, update_network_status, get_tickets, PopulateRooms,
                   UpdateRoom, RemoveRoom, RetrieveRoomForm, update_csd_domain)
from .permissions import ticket_access, rooms_access, rooms_modify_access, csd_assignment_access
from .views import IndexView, RoomsView, TicketSummaryView, CSDDomainAssignmentEditView, report_outage


app_name = 'core'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url=static('images/icons/favicon.ico'), permanent=True), name='favicon'),
    url(r'^robots\.txt$', RedirectView.as_view(url=static('robots.txt'), permanent=True), name='robots'),
    url(r'^login/$', auth_login, name='login'),
    url(r'^logout/$', auth_logout, name='logout', kwargs={'next_page': settings.CAS_LOGOUT_URL}),

    url(r'^jsreverse/$', cache_page(3600)(urls_js), name='js_reverse'),

    url(r'^ajax/chained_building/$', BuildingChainedAjaxView.as_view(), name='chained_building'),
    url(r'^ajax/chained_room/$', RoomChainedAjaxView.as_view(), name='chained_room'),
    url(r'^ajax/chained_sub_department/$', SubDepartmentChainedAjaxView.as_view(), name='chained_sub_department'),

    url(r'^core/network_status/update/$', update_network_status, name='update_network_status'),

    url(r'^core/tickets/list/$', login_required(ticket_access(get_tickets)), name='get_tickets'),
    url(r'^core/tickets/list/(?P<ticket_id>\b[0-9]*\b)/$', login_required(ticket_access(TicketSummaryView.as_view())), name='ticket_summary'),

    url(r'^rooms/$', login_required(rooms_access(RoomsView.as_view())), name='rooms'),
    url(r'^rooms/populate/$', login_required(rooms_access(PopulateRooms.as_view())), name='populate_rooms'),
    url(r'^rooms/update/$', login_required(rooms_modify_access(UpdateRoom.as_view())), name='update_room'),

    url(r'^rooms/remove/$', login_required(rooms_modify_access(RemoveRoom.as_view())), name='remove_room'),
    url(r'^rooms/form/$', login_required(rooms_modify_access(RetrieveRoomForm.as_view())), name='form_room'),

    url(r'^csd/assign_domain/$', login_required(csd_assignment_access(CSDDomainAssignmentEditView.as_view())), name='csd_assign_domain'),
    url(r'^csd/assign_domain/update/$', login_required(csd_assignment_access(update_csd_domain)), name='update_csd_domain'),

    url(r'^outage/', view=report_outage)

]
