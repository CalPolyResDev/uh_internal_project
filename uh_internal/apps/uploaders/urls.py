"""
.. module:: resnet_internal.apps.uploaders.urls
   :synopsis: University Housing Internal Uploaders URLs

.. moduleauthor:: Kyle Reis <FedoraReis@gmail.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import uploader_access
from .ajax import log_uploader


app_name = 'uploaders'

urlpatterns = [
    url(r'^log_upload/$', log_uploader, name='log_uploader'),
    # url(r'^$', login_required(uploader_access(UploaderView.as_view())), name='home'),
]
