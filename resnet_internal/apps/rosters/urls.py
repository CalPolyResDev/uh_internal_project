"""
.. module:: resnet_internal.apps.rosters.urls
   :synopsis: University Housing Internal Rosters URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import RosterGenerateView

app_name = 'rosters'

urlpatterns = [
    url(r'^$', login_required(RosterGenerateView.as_view()), name='generate')
]
