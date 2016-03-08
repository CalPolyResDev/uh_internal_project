"""
.. module:: resnet_internal.apps.portmap.urls
   :synopsis: University Housing Internal Portmap URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import network_access, network_modify_access
from .ajax import (PopulatePorts, UpdatePort, RetrievePortForm, change_port_status, RemovePort, PortChainedAjaxView,
                   PopulateAccessPoints, UpdateAccessPoint, RetrieveAccessPointForm, RemoveAccessPoint)
from .views import PortsView, PortFrameView, AccessPointsView, AccessPointFrameView

app_name = 'network'

urlpatterns = [
    url(r'^ports/$', login_required(network_access(PortsView.as_view())), name='ports'),
    url(r'^ports/populate/$', login_required(network_access(PopulatePorts.as_view())), name='populate_ports'),
    url(r'^ports/update/$', login_required(network_modify_access(UpdatePort.as_view())), name='update_port'),
    url(r'^ports/form/$', login_required(network_access(RetrievePortForm.as_view())), name='form_port'),
    url(r'^ports/change_status/$', login_required(network_modify_access(change_port_status)), name='change_port_status'),
    url(r'^ports/remove/$', login_required(network_modify_access(RemovePort.as_view())), name='remove_port'),

    url(r'^ports/info_frame/(?P<pk>\b[0-9]+\b)/$', login_required(network_access(PortFrameView.as_view())), name='port_info_frame'),
    url(r'^ports/ajax/chained_port/$', PortChainedAjaxView.as_view(), name='ports_chained_port'),

    url(r'^access-points/$', login_required(network_access(AccessPointsView.as_view())), name='access_points'),
    url(r'^access-points/populate/$', login_required(network_access(PopulateAccessPoints.as_view())), name='populate_access_points'),
    url(r'^access-points/update/$', login_required(network_modify_access(UpdateAccessPoint.as_view())), name='update_access_point'),
    url(r'^access-points/form/$', login_required(network_access(RetrieveAccessPointForm.as_view())), name='form_access_point'),
    url(r'^access-points/remove/$', login_required(network_modify_access(RemoveAccessPoint.as_view())), name='remove_access_point'),
    url(r'^access-points/info_frame/(?P<pk>\b[0-9]+\b)/$', login_required(network_access(AccessPointFrameView.as_view())), name='access_point_info_frame'),
]
