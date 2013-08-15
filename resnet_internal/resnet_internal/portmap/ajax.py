"""
.. module:: resnet_internal.portmap.ajax
   :synopsis: ResNet Internal Residence Halls Port Map AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.conf import settings

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from .models import ResHallWired

logger = logging.getLogger(__name__)


@dajaxice_register
def modify_port(request, request_dict, row_id, row_zero, username):
    dajax = Dajax()

    # Add a temporary loading image to the first column in the edited row
    dajax.assign("#%s:eq(0)" % row_id, 'innerHTML', '<img src="%simages/datatables/load.gif" />' % settings.STATIC_URL)

    # Update the database
    port_instance = ResHallWired.objects.get(id=row_id)

    for column, value in request_dict.items():
        setattr(port_instance, column, value)

    port_instance.save()

    # Log the action
    logger.info("User %s modified port (id='%s') with the following data: %s" % (username, row_id, request_dict))

    # Update the table
    for column, value in request_dict.items():
        if column == "switch_ip":
            dajax.assign("#%s[column='%s'] .display_data a" % (row_id, column), 'href', '/frame/cisco/%s/' % value)
            dajax.assign("#%s[column='%s'] .display_data a" % (row_id, column), 'innerHTML', value)
        else:
            dajax.assign("#%s[column='%s'] .display_data" % (row_id, column), 'innerHTML', value)

    dajax.assign("#%s:eq(0)" % row_id, 'innerHTML', row_zero)

    return dajax.json()
