"""
.. module:: resnet_internal.urls
   :synopsis: ResNet Internal URLs.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.templatetags.staticfiles import static as staticfiles
from django.core.exceptions import PermissionDenied
from django.views.defaults import permission_denied, page_not_found
from django.views.generic import RedirectView

from .apps.adgroups.ajax import remove_resnet_tech
from .apps.adgroups.views import ResTechListEditView
from .apps.computers.ajax import PopulateComputers, UpdateComputer, update_sub_department, remove_computer, remove_pinhole, remove_domain_name
from .apps.computers.views import ComputersView, ComputerRecordsView, RDPRequestView, PinholeRequestView, DomainNameRequestView
from .apps.core.ajax import update_building, update_network_status, get_tickets
from .apps.core.views import IndexView, LoginView, logout, handler500, TicketSummaryView
from .apps.dailyduties.ajax import refresh_duties, update_duty, remove_voicemail, get_email_folders, get_mailbox_summary, email_mark_unread, email_mark_read, email_archive
from .apps.dailyduties.views import VoicemailListView, VoicemailAttachmentRequestView, EmailMessageView, EmailListView, EmailAttachmentRequestView
from .apps.orientation.ajax import complete_task, complete_orientation
from .apps.orientation.views import ChecklistView, OnityDoorAccessView, SRSAccessView, PayrollView
from .apps.portmap.ajax import PopulateResidenceHallWiredPorts, UpdateResidenceHallWiredPort, change_port_status
from .apps.portmap.views import ResidenceHallWiredPortsView
from .apps.printerrequests.ajax import change_request_status, update_part_inventory, update_toner_inventory
from .apps.printerrequests.views import RequestsListView, InventoryView, OnOrderView
from .apps.printers.ajax import PopulatePrinters, UpdatePrinter, remove_printer
from .apps.printers.views import PrintersView
from .settings.base import (technician_access_test, staff_access_test, printers_access_test, printers_modify_access_test,
                            portmap_access_test, portmap_modify_access_test, computers_access_test, computers_modify_access_test,
                            computer_record_modify_access_test)


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
portmap_modify_access = permissions_check(portmap_modify_access_test)

computers_access = permissions_check(computers_access_test)
computers_modify_access = permissions_check(computers_modify_access_test)
computer_record_modify_access = permissions_check(computer_record_modify_access_test)

printers_access = permissions_check(printers_access_test)
printers_modify_access = permissions_check(printers_modify_access_test)

admin.autodiscover()

handler500 = handler500

logger = logging.getLogger(__name__)

# Core
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url=staticfiles('images/icons/favicon.ico')), name='favicon'),
    url(r'^flugzeug/', include(admin.site.urls)),  # admin site urls, masked
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^ajax/update_building/$', update_building, name='ajax_update_building'),
    url(r'^core/network_status/update/$', update_network_status, name='core_update_network_status'),
    url(r'^core/tickets/list/$', login_required(technician_access(get_tickets)), name='core_get_tickets'),
    url(r'^core/tickets/list/(?P<ticket_id>\b[0-9]*\b)/$', login_required(technician_access(TicketSummaryView.as_view())), name='core_ticket_summary'),
]

# Daily Duties
urlpatterns += [
    url(r'^daily_duties/email/list/$', login_required(technician_access(EmailListView.as_view())), name='email_list'),
    url(r'^daily_duties/email/view/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/$', login_required(technician_access(EmailMessageView.as_view())), name='email_view_message'),
    url(r'^daily_duties/email/mark_unread/$', login_required(technician_access(email_mark_unread)), name='email_mark_unread'),
    url(r'^daily_duties/email/mark_read/$', login_required(technician_access(email_mark_read)), name='email_mark_read'),
    url(r'^daily_duties/email/archive$', login_required(technician_access(email_archive)), name='email_archive'),
    url(r'^daily_duties/email/get_attachment/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/(?P<attachment_index>[0-9]+)/$', login_required(technician_access(EmailAttachmentRequestView.as_view())), name='email_get_attachment'),
    url(r'^daily_duties/email/get_folders/$', login_required(technician_access(get_email_folders)), name='email_get_folders'),
    url(r'^daily_duties/email/get_mailbox_summary/$', login_required(technician_access(get_mailbox_summary)), name='email_get_mailbox_summary'),
    url(r'^daily_duties/voicemail_list/$', login_required(technician_access(VoicemailListView.as_view())), name='voicemail_list'),
    url(r'^daily_duties/refresh_duties/$', login_required(technician_access(refresh_duties)), name='daily_duties_refresh_duties'),
    url(r'^daily_duties/update_duty/$', login_required(technician_access(update_duty)), name='daily_duties_update_duty'),
    url(r"^daily_duties/voicemail/(?P<message_uid>\b[0-9]*\b)/$", login_required(technician_access(VoicemailAttachmentRequestView.as_view())), name='voicemail_attachment_request'),
    url(r"^daily_duties/remove_voicemail/$", login_required(technician_access(remove_voicemail)), name='remove_voicemail'),
]

# ResNet Technician Orientation
urlpatterns += [
    url(r'^orientation/$', login_required(technician_access(ChecklistView.as_view())), name='orientation_checklist'),
    url(r'^orientation/payroll/$', login_required(technician_access(PayrollView.as_view())), name='orientation_payroll'),
    url(r'^orientation/onity/$', login_required(technician_access(OnityDoorAccessView.as_view())), name='orientation_onity'),
    url(r'^orientation/srs/$', login_required(technician_access(SRSAccessView.as_view())), name='orientation_srs'),
    url(r'^orientation/complete_task/$', login_required(technician_access(complete_task)), name='orientation_complete_task'),
    url(r'^orientation/complete_orientation/$', login_required(technician_access(complete_orientation)), name='orientation_complete'),
]

# AD Group management
urlpatterns += [
    url(r'^manage/technicians/$', login_required(staff_access(ResTechListEditView.as_view())), name='restech_list_edit'),
    url(r'^manage/technicians/remove/$', login_required(staff_access(remove_resnet_tech)), name='remove_resnet_tech'),
]

# University Housing Computer Index
urlpatterns += [
    url(r'^computers/$', login_required(computers_access(ComputersView.as_view())), name='uh_computers'),
    url(r'^computers/populate/$', login_required(computers_access(PopulateComputers.as_view())), name='populate_uh_computers'),
    url(r'^computers/update/$', login_required(computers_modify_access(UpdateComputer.as_view())), name='update_uh_computer'),
    url(r'^computers/remove/$', login_required(computers_modify_access(remove_computer)), name='remove_uh_computer'),
    url(r'^computers/remove_pinhole/$', login_required(computer_record_modify_access(remove_pinhole)), name='remove_uh_computer_pinhole'),
    url(r'^computers/remove_domain_name/$', login_required(computer_record_modify_access(remove_domain_name)), name='remove_uh_computer_domain_name'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', login_required(computers_access(ComputerRecordsView.as_view())), name='view_uh_computer_record'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/rdp/$', login_required(computers_access(RDPRequestView.as_view())), name='rdp_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/pinhole_request/$', login_required(computer_record_modify_access(PinholeRequestView.as_view())), name='pinhole_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/domain_name_request/$', login_required(computer_record_modify_access(DomainNameRequestView.as_view())), name='domain_name_request'),
    url(r'^computers/ajax/update_sub_department/$', update_sub_department, name='ajax_update_sub_department'),
]

# Printer Requests
urlpatterns += [
    url(r'^printers/requests/list/', login_required(technician_access(RequestsListView.as_view())), name='printer_request_list'),
    url(r'^printers/requests/view_inventory/', login_required(technician_access(InventoryView.as_view())), name='printer_inventory'),
    url(r'^printers/requests/view_ordered/', login_required(technician_access(OnOrderView.as_view())), name='printer_ordered_items'),
    url(r'^printers/requests/change_status/', login_required(technician_access(change_request_status)), name='change_printer_request_status'),
    url(r'^printers/requests/toner/update_inventory/', login_required(technician_access(update_toner_inventory)), name='update_printer_toner_inventory'),
    url(r'^printers/requests/parts/update_inventory/', login_required(technician_access(update_part_inventory)), name='update_printer_part_inventory'),
]

# Univeristy Housing Printer Index
urlpatterns += [
    url(r'^printers/$', login_required(printers_access(PrintersView.as_view())), name='uh_printers'),
    url(r'^printers/populate/$', login_required(printers_access(PopulatePrinters.as_view())), name='populate_uh_printers'),
    url(r'^printers/update/$', login_required(printers_access(UpdatePrinter.as_view())), name='update_uh_printer'),
    url(r'^printers/remove/$', login_required(printers_modify_access(remove_printer)), name='remove_uh_printer'),
]

# Residence Halls Wired Port Map
urlpatterns += [
    url(r'^portmap/$', login_required(portmap_access(ResidenceHallWiredPortsView.as_view())), name='residence_halls_wired_ports'),
    url(r'^portmap/populate/$', login_required(portmap_access(PopulateResidenceHallWiredPorts.as_view())), name='populate_residence_halls_wired_ports'),
    url(r'^portmap/update/$', login_required(portmap_access(UpdateResidenceHallWiredPort.as_view())), name='update_residence_halls_wired_port'),
    url(r'^portmap/change_status/$', login_required(portmap_modify_access(change_port_status)), name='change_residence_halls_wired_port_status'),
]

# Raise errors on purpose
urlpatterns += [
    url(r'^500/$', handler500),
    url(r'^403/$', permission_denied),
    url(r'^404/$', page_not_found),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
