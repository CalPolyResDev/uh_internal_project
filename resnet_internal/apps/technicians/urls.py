"""
.. module:: resnet_internal.apps.adgroups.urls
   :synopsis: University Housing Internal AD Groups URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import technician_list_access
from .ajax import remove_resnet_tech
from .views import ResTechListEditView


app_name = 'technicians'

urlpatterns = [
    url(r'^$', login_required(technician_list_access(ResTechListEditView.as_view())), name='home'),
    url(r'^remove/$', login_required(technician_list_access(remove_resnet_tech)), name='remove'),
]
