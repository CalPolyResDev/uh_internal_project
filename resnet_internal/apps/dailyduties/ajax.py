"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: ResNet Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from datetime import datetime

from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax

from .models import DailyDuties
from .utils import GetDutyData, VoicemailManager

logger = logging.getLogger(__name__)


@ajax
def refresh_duties(request):

    # Load data dicts
    printer_requests_dict = GetDutyData().get_printer_requests()
    voicemail_dict = GetDutyData().get_messages()
    email_dict = GetDutyData().get_email()
    tickets_dict = GetDutyData().get_tickets(request.user)
    
    printer_requests_text = 'Printer Requests (' + str(printer_requests_dict['count']) + ')'
    voicemail_text = 'Voicemail (' + str(voicemail_dict['count']) + ')'
    email_text = 'Email (' + str(email_dict['count']) + ')'
    ticket_text = 'Ticket Manager (' + str(tickets_dict['count']) + ')'
    
    def duty_dict_to_popover_html(daily_duty_dict):
        popover_html = """
            Last Checked:
            <font color='""" + daily_duty_dict["status_color"] + """'>""" + daily_duty_dict["last_checked"] + """</font>
            <br />
            (""" + daily_duty_dict["last_user"] + """)
            """
        return popover_html

    data = {
        'inner-fragments': {
            '#printer_requests_text': printer_requests_text,
            '#voicemail_text': voicemail_text,
            '#email_text': email_text,
            '#ticket_text': ticket_text,
        },
        'printer_requests_content': duty_dict_to_popover_html(printer_requests_dict),
        'voicemail_content': duty_dict_to_popover_html(voicemail_dict),
        'email_content': duty_dict_to_popover_html(email_dict),
        'tickets_content': duty_dict_to_popover_html(tickets_dict),
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

    :param message_uuid: The voicemail's uuid.
    :type message_uuid: int

    """
    # Pull post parameters
    message_uuid = request.POST["message_uuid"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["message_uuid"] = message_uuid

    with VoicemailManager() as voicemail_manager:
        voicemail_manager.delete_message(message_uuid)

    return context
