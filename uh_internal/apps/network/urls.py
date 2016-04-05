"""
.. module:: resnet_internal.apps.network.urls
   :synopsis: University Housing Internal Network URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import network_access, network_modify_access
from .ajax import (PopulatePorts, UpdatePort, RetrievePortForm, change_port_status, RemovePort, PortChainedAjaxView,
                   PopulateAccessPoints, UpdateAccessPoint, RetrieveAccessPointForm, RemoveAccessPoint,
                   PopulateNetworkInfrastructureDevices, UpdateNetworkInfrastructureDevice, RetrieveNetworkInfrastructureDeviceForm, RemoveNetworkInfrastructureDevice)
from .views import PortsView, PortFrameView, AccessPointsView, AccessPointFrameView, NetworkInfrastructureDevicesView, DeviceStatusView, OverallBandwidthReportView, DeviceBandwidthReportView, OverallClientReportView, LoginAttemptInfoFrameView, ClientBandwidthReportView, TroubleshooterView
from uh_internal.apps.network.views import TroubleshooterReportView


app_name = 'network'

urlpatterns = [
    url(r'^troubleshooter/$', login_required(network_access(TroubleshooterView.as_view())), name='troubleshooter'),
    url(r'^troubleshooter/report/(?P<user_query>.*?)/$', login_required(network_access(TroubleshooterReportView.as_view())), name='troubleshooter_report'),

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

    url(r'^airwaves/device_status_frame/(?P<id>\b[0-9]+\b)/$', login_required(network_access(DeviceStatusView.as_view())), name='airwaves_device_status'),
    url(r'^airwaves/device_bandwidth/(?P<id>\b[0-9]+\b)/(?P<device_type>\b[A-Za-z ]+\b)/$', login_required(network_access(DeviceBandwidthReportView.as_view())), name='airwaves_device_bandwidth'),
    url(r'^airwaves/client_bandwidth/(?P<mac_address>\b[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\2[0-9a-f]{2}){4}\b)/$', login_required(network_access(ClientBandwidthReportView.as_view())), name='airwaves_client_bandwidth'),
    url(r'^airwaves/overall_bandwidth/$', login_required(network_access(OverallBandwidthReportView.as_view())), name='airwaves_overall_bandwidth'),
    url(r'^airwaves/overall_clients/$', login_required(network_access(OverallClientReportView.as_view())), name='airwaves_overall_clients'),

    url(r'^clearpass/attempt_info_frame/(?P<pk>\b[0-9]+\b)/$', login_required(network_access(LoginAttemptInfoFrameView.as_view())), name='login_attempt_info_frame'),

    url(r'^network-infrastructure-devices/$', login_required(network_access(NetworkInfrastructureDevicesView.as_view())), name='network_infrastructure_devices'),
    url(r'^network-infrastructure-devices/populate/$', login_required(network_access(PopulateNetworkInfrastructureDevices.as_view())), name='populate_network_infrastructure_devices'),
    url(r'^network-infrastructure-devices/update/$', login_required(network_modify_access(UpdateNetworkInfrastructureDevice.as_view())), name='update_network_infrastructure_device'),
    url(r'^network-infrastructure-devices/form/$', login_required(network_access(RetrieveNetworkInfrastructureDeviceForm.as_view())), name='form_network_infrastructure_device'),
    url(r'^network-infrastructure-devices/remove/$', login_required(network_modify_access(RemoveNetworkInfrastructureDevice.as_view())), name='remove_network_infrastructure_device'),
]
