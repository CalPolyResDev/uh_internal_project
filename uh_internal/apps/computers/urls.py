"""
.. module:: resnet_internal.apps.computers.urls
   :synopsis: University Housing Internal Computers URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import computer_record_modify_access, computers_access, computers_modify_access
from .views import ComputersView, PopulateComputers, ComputerRecordsView, RDPRequestView, PinholeRequestView, DomainNameRequestView
from .ajax import UpdateComputer, RetrieveComputerForm, RemoveComputer, remove_pinhole, remove_domain_name

app_name = 'computers'

urlpatterns = [
    url(r'^$', login_required(computers_access(ComputersView.as_view())), name='home'),
    url(r'^populate/$', login_required(computers_access(PopulateComputers.as_view())), name='populate'),
    url(r'^update/$', login_required(computers_modify_access(UpdateComputer.as_view())), name='update'),
    url(r'^form/$', login_required(computers_modify_access(RetrieveComputerForm.as_view())), name='form'),
    url(r'^remove/$', login_required(computers_modify_access(RemoveComputer.as_view())), name='remove'),
    url(r'^remove_pinhole/$', login_required(computer_record_modify_access(remove_pinhole)), name='remove_pinhole'),
    url(r'^remove_domain_name/$', login_required(computer_record_modify_access(remove_domain_name)), name='remove_domain_name'),
    url(r'^(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', login_required(computers_access(ComputerRecordsView.as_view())), name='view_record'),
    url(r'^(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/rdp/$', login_required(computers_access(RDPRequestView.as_view())), name='rdp_request'),
    url(r'^(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/pinhole_request/$', login_required(computer_record_modify_access(PinholeRequestView.as_view())), name='pinhole_request'),
    url(r'^(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/domain_name_request/$', login_required(computer_record_modify_access(DomainNameRequestView.as_view())), name='domain_name_request'),
]
