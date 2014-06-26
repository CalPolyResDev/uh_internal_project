"""
.. module:: resnet_internal.orientation.ajax
   :synopsis: ResNet Internal Orientation AJAX URLs.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register


@dajaxice_register
def complete_task(request, task):
    dajax = Dajax()

    user = get_user_model().objects.get(username=request.user.username)

    if task == "onity":
        user.onity_complete = True
    elif task == "srs":
        user.srs_complete = True
    elif task == "payroll":
        user.payroll_complete = True

    user.save()

    dajax.redirect(reverse('orientation_checklist'))

    return dajax.json()


@dajaxice_register
def complete_orientation(request):
    dajax = Dajax()

    user = get_user_model().objects.get(username=request.user.username)
    user.orientation_complete = True
    user.is_new_tech = False
    user.save()

    dajax.redirect(reverse('home'))

    return dajax.json()
