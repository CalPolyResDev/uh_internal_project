"""
.. module:: resnet_internal.apps.uploaders.ajax
   :synopsis: University Housing Internal Uploaders AJAX Methods.

.. moduleauthor:: Kyle Reis <FedoraReis@gmail.com>

"""

from datetime import datetime
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Uploaders

logger = logging.getLogger(__name__)


@api_view(['POST'])
def log_uploader(request):
    """ Log activity for an uploader.

    :param uploader: The name of the uploader.
    :type duty: str
    :param success: Whether the uploader successfully ran.
    :type duty: bool

    """

    # Pull post parameters
    data = request.data

    uploader = Uploaders()
    uploader.name = data["uploader"]
    uploader.last_run = datetime.now()
    uploader.successful = data["success"]
    uploader.save()

    return Response()
