"""
.. module:: resnet_internal.urls
   :synopsis: University Housing Internal URLs.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>
.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import logging

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.defaults import permission_denied, page_not_found

from .apps.core.views import handler500


handler500 = handler500

logger = logging.getLogger(__name__)

urlpatterns = [
    url(r'^technicians/', include('resnet_internal.apps.technicians.urls')),
    url(r'^computers/', include('resnet_internal.apps.computers.urls')),
    url(r'^', include('resnet_internal.apps.core.urls')),
    url(r'^dailyduties/', include('resnet_internal.apps.dailyduties.urls')),
    url(r'^orientation/', include('resnet_internal.apps.orientation.urls')),
    url(r'^network/', include('resnet_internal.apps.portmap.urls')),
    url(r'^printerrequests/', include('resnet_internal.apps.printerrequests.urls')),
    url(r'^printers/', include('resnet_internal.apps.printers.urls')),
    url(r'^residents/', include('resnet_internal.apps.residents.urls')),
    url(r'^rosters/', include('resnet_internal.apps.rosters.urls')),
]


# Raise errors on purpose
urlpatterns += [
    url(r'^500/$', handler500),
    url(r'^403/$', permission_denied),
    url(r'^404/$', page_not_found),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
