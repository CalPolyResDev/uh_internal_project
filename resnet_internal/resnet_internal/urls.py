"""
.. module:: resnet_internal.urls
   :synopsis: ResNet Internal URLs.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.base import TemplateView, RedirectView

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

from .core.views import LoginView
from .orientation.views import OnityDoorAccessView, SRSAccessView
from .computers.views import ComputersView, ComputerRecordsView, PinholeRequestView, DomainNameRequestView
from .portmap.views import ResidenceHallWiredPortsView

admin.autodiscover()
dajaxice_autodiscover()

logger = logging.getLogger(__name__)
orientation_access = user_passes_test(lambda user: user.is_developer or user.is_technician)
computers_access = user_passes_test(lambda user: user.is_developer or user.is_rn_staff or user.is_technician or user.is_domain_manager or user.is_net_admin or user.is_tag)
portmap_access = user_passes_test(lambda user: user.is_developer or user.is_rn_staff or user.is_technician or user.is_net_admin or user.is_tag or user.is_telecom)


# Core
urlpatterns = patterns('core.views',
    url(r'^$', TemplateView.as_view(template_name='core/index.html'), name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='%simages/icons/favicon.ico' % settings.STATIC_URL), name='favicon'),
    url(r'^flugzeug/', include(admin.site.urls), name='admin'),  # admin site urls, masked
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^(?P<mode>frame|external)/(?P<key>\b[a-zA-Z0-9]*\b)/$', 'link_handler', name='link_handler'),
    url(r'^(?P<mode>frame|external)/(?P<key>cisco)/(?P<ip>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', 'link_handler', name='link_handler_cisco'),
)

# ResNet Technician Orientation
urlpatterns += patterns('',
    url(r'^orientation/$', login_required(orientation_access(TemplateView.as_view(template_name='orientation/checklist.html'))), name='orientation-checklist'),
    url(r'^orientation/onity$', login_required(orientation_access(OnityDoorAccessView.as_view())), name='orientation-onity'),
    url(r'^orientation/srs$', login_required(orientation_access(SRSAccessView.as_view())), name='orientation-srs'),
    url(r'^orientation/payroll$', login_required(orientation_access(TemplateView.as_view(template_name='orientation/payrollAccess.html'))), name='orientation-payroll'),
)

# Residence Halls Wired Port Map
urlpatterns += patterns('',
    url(r'^portmap/$', login_required(portmap_access(TemplateView.as_view(template_name='portmap/portmap.html'))), name='residence_halls_wired_ports'),
    url(r'^portmap/populate/$', login_required(portmap_access(ResidenceHallWiredPortsView.as_view())), name='populate_residence_halls_wired_ports'),
)

# Univeristy Housing Computer Index
urlpatterns += patterns('',
    url(r'^computers/$', login_required(computers_access(TemplateView.as_view(template_name='computers/computers.html'))), name='uh_computers'),
    url(r'^computers/populate/$', login_required(computers_access(ComputersView.as_view())), name='populate_uh_computers'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', login_required(computers_access(ComputerRecordsView.as_view())), name='view_uh_computer_record'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/pinhole_request/$', login_required(computers_access(PinholeRequestView.as_view())), name='pinhole_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/domain_name_request/$', login_required(computers_access(DomainNameRequestView.as_view())), name='domain_name_request'),
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
    # The following should align with the DAJAXICE_MEDIA_PREFIX setting
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
