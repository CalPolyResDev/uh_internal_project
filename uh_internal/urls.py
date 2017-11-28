"""
.. module:: resnet_internal.urls
   :synopsis: University Housing Internal URLs.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>
.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import logging

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.defaults import permission_denied, page_not_found

from .settings.base import MAIN_APP_NAME
from .apps.core.views import handler500


handler500 = handler500

logger = logging.getLogger(__name__)

urlpatterns = [
    url(r'^flugzeug/', include(admin.site.urls)),  # admin site urls, masked
    url(r'^technicians/', include(MAIN_APP_NAME + '.apps.technicians.urls')),
    url(r'^computers/', include(MAIN_APP_NAME + '.apps.computers.urls')),
    url(r'^dailyduties/', include(MAIN_APP_NAME + '.apps.dailyduties.urls')),
    url(r'^orientation/', include(MAIN_APP_NAME + '.apps.orientation.urls')),
    url(r'^network/', include(MAIN_APP_NAME + '.apps.network.urls')),
    url(r'^printerrequests/', include(MAIN_APP_NAME + '.apps.printerrequests.urls')),
    url(r'^printers/', include(MAIN_APP_NAME + '.apps.printers.urls')),
    url(r'^residents/', include(MAIN_APP_NAME + '.apps.residents.urls')),
    url(r'^rosters/', include(MAIN_APP_NAME + '.apps.rosters.urls')),
    url(r'^', include(MAIN_APP_NAME + '.apps.core.urls')),
]


# Raise errors on purpose
urlpatterns += [
    url(r'^500/$', handler500),
    url(r'^403/$', permission_denied),
    url(r'^404/$', page_not_found),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
