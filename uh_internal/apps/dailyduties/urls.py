"""
.. module:: resnet_internal.apps.dailyduties.urls
   :synopsis: University Housing Internal Daily Duties URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import daily_duties_access
from .ajax import refresh_duties, update_duty


app_name = 'dailyduties'

urlpatterns = [
    url(r'^refresh_duties/$',
        login_required(daily_duties_access(refresh_duties)),
        name='refresh_duties'),
    url(r'^update_duty/$',
        login_required(daily_duties_access(update_duty)),
        name='update_duty'),
]
