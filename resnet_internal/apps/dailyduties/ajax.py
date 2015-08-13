"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: ResNet Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax

from .models import DailyDuties
from .utils import GetDutyData
from resnet_internal.apps.dailyduties.utils import VoicemailManager

logger = logging.getLogger(__name__)


@ajax
def refresh_duties(request):

    # Load data dicts
    printer_requests_dict = GetDutyData().get_printer_requests()
    messages_dict = GetDutyData().get_messages()
    email_dict = GetDutyData().get_email()
    tickets_dict = GetDutyData().get_tickets(request.user)

    if printer_requests_dict["count"] >= 0:
        printer_request_count = ' <b>(' + str(printer_requests_dict["count"]) + ')</b>'
    else:
        printer_request_count = ''

    if messages_dict["count"] >= 0:
        message_count = ' <b>(' + str(messages_dict["count"]) + ')</b>'
    else:
        message_count = ''

    if email_dict["count"] >= 0:
        email_count = ' <b>(' + str(email_dict["count"]) + ')</b>'
    else:
        email_count = ''

    if tickets_dict["count"] >= 0:
        ticket_count = ' <b>(' + str(tickets_dict["count"]) + ')</b>'
    else:
        ticket_count = ''

    duties_html = """
    <h2 class="center">Daily Duties</h2>
    <h3><a style="cursor:pointer;" onclick="updateDuty('printerrequests', '""" + reverse('printer_request_list') + """', '_self')">Check Printer Requests""" + printer_request_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + printer_requests_dict["status_color"] + """'>""" + printer_requests_dict["last_checked"] + """</font>
        <br />
        (""" + printer_requests_dict["last_user"] + """)
    </p>
    <h3><a href='""" + reverse('phone_instructions') + """' class="popup_frame" style="cursor:pointer;" onclick="updateDuty('messages', '', '_self')">Check Voicemail""" + message_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + messages_dict["status_color"] + """'>""" + messages_dict["last_checked"] + """</font>
        <br />
        (""" + messages_dict["last_user"] + """)
    </p>
    <h3><a style="cursor:pointer;" onclick="updateDuty('email', '/external/zimbra/', '_blank')">Check Email""" + email_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + email_dict["status_color"] + """'>""" + email_dict["last_checked"] + """</font>
        <br />
        (""" + email_dict["last_user"] + """)
    </p>
    <h3><a style="cursor:pointer;" onclick="updateDuty('tickets', '/link_handler/srs/', 'handler')">Check Tickets""" + ticket_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + tickets_dict["status_color"] + """'>""" + tickets_dict["last_checked"] + """</font>
        <br />
        (""" + tickets_dict["last_user"] + """)
    </p>
    <h3></h3>
    <p>
        Note: Times update upon click of task title link.
    </p>"""

    data = {
        'inner-fragments': {
            '#dailyDuties': duties_html
        },
    }

    return data


@ajax
@require_POST
def update_duty(request):
    """ Update a particular duty.

    :param duty: The duty to update.
    :type duty: str

    """

    # Pull post parameters
    duty = request.POST["duty"]

    data = DailyDuties.objects.get(name=duty)
    data.last_checked = datetime.now()
    data.last_user = get_user_model().objects.get(username=request.user.username)
    data.save()


@ajax
@require_POST
def remove_voicemail(request):
    """ Removes computers from the computer index if no pinhole/domain name records are associated with it.

    :param vm_uuid: The vm's id.
    :type vm_uuid: int

    """
    # Pull post parameters
    message_uuid = request.POST["message_uuid"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["uuid"] = message_uuid

    voicemail_manager = VoicemailManager()
    voicemail_manager.delete_message(message_uuid)
    
    return context
