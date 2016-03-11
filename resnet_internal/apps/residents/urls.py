"""
.. module:: resnet_internal.apps.residents.urls
   :synopsis: University Housing Internal Residents URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import SearchView

app_name = 'residents'

urlpatterns = [
    url(r'^$', login_required(SearchView.as_view()), name='home'),
]
