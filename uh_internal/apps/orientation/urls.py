"""
.. module:: resnet_internal.apps.orientation.urls
   :synopsis: University Housing Internal Orientation URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import orientation_access
from .ajax import complete_task, complete_orientation
from .views import ChecklistView, PayrollView, OnityDoorAccessView, SRSAccessView

app_name = 'orientation'

urlpatterns = [
    url(r'^$',
        login_required(orientation_access(ChecklistView.as_view())),
        name='home'),
    url(r'^payroll/$',
        login_required(orientation_access(PayrollView.as_view())),
        name='payroll'),
    url(r'^onity/$',
        login_required(orientation_access(OnityDoorAccessView.as_view())),
        name='onity'),
    url(r'^srs/$',
        login_required(orientation_access(SRSAccessView.as_view())),
        name='srs'),
    url(r'^complete_task/$',
        login_required(orientation_access(complete_task)),
        name='complete_task'),
    url(r'^complete/$',
        login_required(orientation_access(complete_orientation)),
        name='complete'),
]
