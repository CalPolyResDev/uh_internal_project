"""
.. module:: resnet_internal.portmap.ajax
   :synopsis: ResNet Internal Residence Halls Port Map AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging

from dajax.core import Dajax
from django.contrib.staticfiles.templatetags.staticfiles import static
from dajaxice.decorators import dajaxice_register

from resnet_internal.settings.base import portmap_modify_access_test
from .models import ResHallWired

logger = logging.getLogger(__name__)


@dajaxice_register
def change_port_status(request, port_id):
    """ Activates ports in the portmap index.

    :param port_id: The port's id.
    :type port_id: str

    """

    dajax = Dajax()

    if portmap_modify_access_test(request.user):
        port_instance = ResHallWired.objects.get(id=port_id)
        if port_instance.active:
            port_instance.active = False
        else:
            port_instance.active = True
        port_instance.save()

        # Redraw the table
        dajax.script('residence_halls_wired_port_map.fnDraw();')

    return dajax.json()


@dajaxice_register
def modify_port(request, request_dict, row_id, row_zero, username):
    dajax = Dajax()

    if portmap_modify_access_test(request.user):
        # Add a temporary loading image to the first column in the edited row
        dajax.assign("#%s:eq(0)" % row_id, 'innerHTML', """<img src="{icon_url}" />""".format(icon_url=static('images/datatables/load.gif')))

        # Update the database
        port_instance = ResHallWired.objects.get(id=row_id)

        for column, value in request_dict.items():
            setattr(port_instance, column, value)

        port_instance.save()

        # Redraw the table
        dajax.script('residence_halls_wired_port_map.fnDraw();')

    return dajax.json()
