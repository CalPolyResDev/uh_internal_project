"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: ResNet Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from datetime import datetime

from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.utils.encoding import smart_text
from django.http.response import HttpResponse
from django.template import Template, RequestContext

from django_ajax.decorators import ajax

from .models import DailyDuties
from .utils import GetDutyData, EmailManager

logger = logging.getLogger(__name__)


@ajax
def refresh_duties(request):
    duty_data = cache.get('duty_data')

    if not duty_data:
        with GetDutyData() as duty_data_manager:
            duty_data = {
                'printer_requests': duty_data_manager.get_printer_requests(),
                'voicemail': duty_data_manager.get_messages(),
                'email': duty_data_manager.get_email(),
                'tickets': duty_data_manager.get_tickets(request.user),
            }
            cache.set('duty_data', duty_data, 120)

    def duty_dict_to_link_text(daily_duty_dict, name):
        return_string = name

        if daily_duty_dict['count'] > 10:
            return_string += ' <strong class="text-danger">(' + str(daily_duty_dict['count']) + ')</strong>'
        elif daily_duty_dict['count'] > 0:
            return_string += ' <strong>(' + str(daily_duty_dict['count']) + ')</strong>'

        return return_string

    def duty_dict_to_popover_html(daily_duty_dict):
        popover_html = """
            Last Checked:
            <font color='""" + daily_duty_dict["status_color"] + """'>""" + daily_duty_dict["last_checked"] + """</font>
            <br />
            (<span style='text-align: center;'>""" + daily_duty_dict["last_user"] + """</span>)
            """
        return popover_html

    data = {
        'inner-fragments': {
            '#printer_requests_text': duty_dict_to_link_text(duty_data['printer_requests'], 'Printer Requests'),
            '#voicemail_text': duty_dict_to_link_text(duty_data['voicemail'], 'Voicemail'),
            '#email_text': duty_dict_to_link_text(duty_data['email'], 'Email'),
            '#ticket_text': duty_dict_to_link_text(duty_data['tickets'], 'Ticket Manager'),
        },
        'printer_requests_content': duty_dict_to_popover_html(duty_data['printer_requests']),
        'voicemail_content': duty_dict_to_popover_html(duty_data['voicemail']),
        'email_content': duty_dict_to_popover_html(duty_data['email']),
        'tickets_content': duty_dict_to_popover_html(duty_data['tickets']),
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
    message_uid = request.POST["message_uid"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["message_uid"] = message_uid

    with EmailManager() as email_manager:
        email_manager.delete_voicemail_message(message_uid)

    return context


def get_email_folders(request):
    with EmailManager() as email_manager:
        folder_response = email_manager.server.list_folders()

    html_response = "<ul><li class='jstree-open' id='root'>ResNet Email<ul>"
    current_parents = []
    hide_list = ('Calendar', 'Contacts', 'Journal', 'Notes', 'Tasks', 'Voicemails', 'Archives/Voicemails')

    for flags, delimiter, folder_name in folder_response:
        hierarchical_list = folder_name.split(smart_text(delimiter))

        if current_parents and (len(hierarchical_list) < 2 or not current_parents[-1] == hierarchical_list[-2]):
            html_response += '</li></ul>'
            current_parents.pop()

        if folder_name.startswith(hide_list):
            continue

        if b'\\HasChildren' in flags:
            html_response += "<li class='jstree-closed' id='" + folder_name + "'>" + hierarchical_list[-1]
            html_response += '<ul>'
            current_parents.append(hierarchical_list[-1])
        else:
            html_response += '<li id="' + folder_name + '"' + (" data-jstree='{\"selected\": true}'" if folder_name == 'INBOX' else "") + '>' + hierarchical_list[-1] + '</li>'

    html_response += "</li></ul></ul>"

    return HttpResponse(html_response)

@ajax
@require_POST
def get_mailbox_summary(request):
    mailbox_name = request.POST["mailbox"]

    with EmailManager() as email_manager:
        mailbox_summary = email_manager.get_mailbox_summary(mailbox_name)

    raw_response = """
        {% if emails %}
            {% for email in emails %}
            <tr id="email_{{ email.message_uid }}" {% if email.unread %}class="bg-info"{% endif %}>
                <td>{{ email.date }}</td>
                <td>{{ email.from_name }} &lt;{{email.from_address }}&gt;</td>
                <td>{{ email.subject }}</td>
            </tr>
            {% endfor %}
        {% else %}
        <tr>
            <td colspan="4" style="text-align: center;">There are currently no emails in this mailbox.</td>
        </tr>
        {% endif %}
    """

    template = Template(raw_response)
    context = RequestContext(request, {'emails': mailbox_summary})
    response_html = template.render(context)

    data = {
        'fragments': {
            '#loading_email_record': response_html
        }
    }

    return data
