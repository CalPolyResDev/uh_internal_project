"""
.. module:: resnet_internal.apps.orientation.ajax
   :synopsis: University Housing Internal Orientation AJAX URLs.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view


@api_view(['POST'])
def complete_task(request):
    """ Completes a task.

    :param task: The task to complete.
    :type task: str

    """

    # Pull post parameters
    task = request.data["task"]

    user = get_user_model().objects.get(username=request.user.username)

    if task == "onity":
        user.onity_complete = True
    elif task == "srs":
        from srsconnector.models import AccountRequest
        ticket = AccountRequest(subject_username=request.user.get_alias())
        ticket.save()
        user.srs_complete = True
        from srsconnector.models import AccountRequest
        ticket = AccountRequest(subject_username=request.user.get_alias())
        ticket.save()
    elif task == "payroll":
        user.payroll_complete = True

    user.save()

    return redirect('orientation:home')


@api_view(['GET'])
def complete_orientation(request):
    """ Completes orientation."""

    user = get_user_model().objects.get(username=request.user.username)
    user.orientation_complete = True
    user.is_new_tech = False
    user.save()

    return redirect('core:home')
