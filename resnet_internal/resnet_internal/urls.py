"""
.. module:: resnet_internal.urls
   :synopsis: ResNet Internal URLs.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging

from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import RedirectView

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

from .core.views import IndexView, LoginView, NavigationSettingsView
from .adgroups.views import ResTechListEditView
from .orientation.views import ChecklistView, OnityDoorAccessView, SRSAccessView, PayrollView
from .computers.views import ComputersView, PopulateComputers, ComputerRecordsView, RDPRequestView, PinholeRequestView, DomainNameRequestView
from .portmap.views import ResidenceHallWiredPortsView, PopulateResidenceHallWiredPorts
from .printers.views import RequestsListView, InventoryView, OnOrderView, PrintersView, PopulatePrinters

from resnet_internal.settings.base import technician_access_test, staff_access_test, printers_access_test, portmap_access_test, computers_access_test, computer_record_modify_access_test


def permissions_check(test_func, raise_exception=True):
    """
    Decorator for views that checks whether a user has permission to view the
    requested page, redirecting to the log-in page if neccesary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.

    :param test_func: A callable test that takes a User object and returns true if the test passes.
    :type test_func: callable
    :param raise_exception: Determines whether or not to throw an exception when permissions test fails.
    :type raise_exception: bool

    """

    def check_perms(user):
        # First check if the user has the permission (even anon users)
        if test_func(user):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms)

technician_access = permissions_check(technician_access_test)
staff_access = permissions_check(staff_access_test)

portmap_access = permissions_check(portmap_access_test)

computers_access = permissions_check(computers_access_test)
computer_record_modify_access = permissions_check(computer_record_modify_access_test)

printers_access = permissions_check(printers_access_test)

admin.autodiscover()
dajaxice_autodiscover()

logger = logging.getLogger(__name__)

# Core
urlpatterns = patterns('core.views',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='%simages/icons/favicon.ico' % settings.STATIC_URL), name='favicon'),
    url(r'^flugzeug/', include(admin.site.urls)),  # admin site urls, masked
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^settings/navigation/$', login_required(NavigationSettingsView.as_view()), name='navigation_settings'),
    url(r'^(?P<mode>frame|external|link_handler)/(?P<key>\b[a-zA-Z0-9_]*\b)/$', 'link_handler', name='link_handler'),
    url(r'^(?P<mode>frame|external|link_handler)/(?P<key>cisco)/(?P<ip>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', 'link_handler', name='link_handler_cisco'),
)

# ResNet Technician Orientation
urlpatterns += patterns('',
    url(r'^orientation/$', login_required(technician_access(ChecklistView.as_view())), name='orientation_checklist'),
    url(r'^orientation/onity$', login_required(technician_access(OnityDoorAccessView.as_view())), name='orientation_onity'),
    url(r'^orientation/srs$', login_required(technician_access(SRSAccessView.as_view())), name='orientation_srs'),
    url(r'^orientation/payroll$', login_required(technician_access(PayrollView.as_view())), name='orientation_payroll'),
)

# AD Group management
urlpatterns += patterns('',
    url(r'^manage/technicians/$', login_required(staff_access(ResTechListEditView.as_view())), name='restech_list_edit'),
)

# Printer Requests
urlpatterns += patterns('',
    url(r'^printers/view_requests', login_required(technician_access(RequestsListView.as_view())), name='printer_request_list'),
    url(r'^printers/view_inventory', login_required(technician_access(InventoryView.as_view())), name='printer_inventory'),
    url(r'^printers/view_ordered', login_required(technician_access(OnOrderView.as_view())), name='printer_ordered_items'),
)

# Univeristy Housing Printer Index
urlpatterns += patterns('',
    url(r'^printers/$', login_required(printers_access(PrintersView.as_view())), name='uh_printers'),
    url(r'^printers/populate/$', login_required(printers_access(PopulatePrinters.as_view())), name='populate_uh_printers'),
)

# Residence Halls Wired Port Map
urlpatterns += patterns('',
    url(r'^portmap/$', login_required(portmap_access(ResidenceHallWiredPortsView.as_view())), name='residence_halls_wired_ports'),
    url(r'^portmap/populate/$', login_required(portmap_access(PopulateResidenceHallWiredPorts.as_view())), name='populate_residence_halls_wired_ports'),
)

# Univeristy Housing Computer Index
urlpatterns += patterns('',
    url(r'^computers/$', login_required(computers_access(ComputersView.as_view())), name='uh_computers'),
    url(r'^computers/populate/$', login_required(computers_access(PopulateComputers.as_view())), name='populate_uh_computers'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', login_required(computers_access(ComputerRecordsView.as_view())), name='view_uh_computer_record'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/rdp/$', login_required(computers_access(RDPRequestView.as_view())), name='rdp_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/pinhole_request/$', login_required(computer_record_modify_access(PinholeRequestView.as_view())), name='pinhole_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/domain_name_request/$', login_required(computer_record_modify_access(DomainNameRequestView.as_view())), name='domain_name_request'),
)

# jCal (hours schedule)
# urlpatterns += patterns('jCal.views',
#    url(r'^jCal/$', 'jCal_home'),
#    url(r'^jCal/my_schedule/(?P<year>\d{4})/(?P<quarter>[a-z]{2})/(?P<office>[a-z]{2})/(?P<is_finals>\d{1})/$', 'my_schedule'),
#    url(r'^jCal/global_schedule/(?P<year>\d{4})/(?P<quarter>[a-z]{2})/(?P<office>[a-z]{2})/(?P<is_finals>\d{1})/$', 'global_schedule'),
#    url(r'^jCal/set_avail/$', 'set_avail'),
    # this will send you to a page to set year/quarter/is_finals, on submit will redirect you to jCal/set_avail/year/quarter/is_finals
#    url(r'^jCal/set_avail/(?P<year>\d{4})/(?P<quarter>[a-z]{2})/(?P<is_finals>\d{1})/$', 'set_avail'),
#    url(r'^jCal/jCal_admin/$', 'jCal_admin'),
# )
# (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'news.views.article_detail'),
# news.views.article_detail(request, year='2003', month='03', day='03').
# (?P<month>[a-z]{3})

# Dajaxice
urlpatterns += patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
