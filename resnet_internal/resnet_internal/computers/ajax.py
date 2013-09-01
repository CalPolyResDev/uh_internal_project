"""
.. module:: resnet_internal.computers.ajax
   :synopsis: ResNet Internal Computer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.conf import settings

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from .models import Computer

logger = logging.getLogger(__name__)


@dajaxice_register
def modify_computer(request, request_dict, row_id, row_zero, username):
    dajax = Dajax()

    # Add a temporary loading image to the first column in the edited row
    dajax.assign("#%s:eq(0)" % row_id, 'innerHTML', '<img src="%simages/datatables/load.gif" />' % settings.STATIC_URL)

    # Update the database
    port_instance = Computer.objects.get(id=row_id)

    for column, value in request_dict.items():
        setattr(port_instance, column, value)

    port_instance.save()

    # Log the action
    logger.info("User %s modified computer (id='%s') with the following data: %s" % (username, row_id, request_dict))

    # Update the table
    for column, value in request_dict.items():
        dajax.assign("#%s[column='%s'] .display_data" % (row_id, column), 'innerHTML', value)

    dajax.assign("#%s:eq(0)" % row_id, 'innerHTML', row_zero)

    return dajax.json()
