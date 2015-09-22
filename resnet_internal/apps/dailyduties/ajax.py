"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: ResNet Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import datetime
import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http.response import HttpResponse
from django.template import Template, RequestContext
from django.utils.encoding import smart_text
from django.views.decorators.http import require_POST
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
                'voicemail': duty_data_manager.get_voicemail(),
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
            <font color='""" + str(daily_duty_dict["status_color"]) + """'>""" + str(daily_duty_dict["last_checked"]) + """</font>
            <br />
            (<span style='text-align: center;'>""" + str(daily_duty_dict["last_user"]) + """</span>)
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

    if mailbox_name == 'root':
        mailbox_summary = None
    else:
        with EmailManager() as email_manager:
            mailbox_summary = email_manager.get_mailbox_summary(mailbox_name)

    raw_response = """
        {% load staticfiles %}
        {% if emails %}
            {% for email in emails %}
            <tr id="{{ mailbox_name }}/{{ email.uid }}" {% if email.unread %}class="bg-info"{% endif %}>
                <td>
                    <input type="checkbox" name="email_selection" value="{{ email.uid }}" id="checkbox_{{ mailbox_name }}/{{ email.uid }}">
                    <div id="spinner_{{ mailbox_name }}/{{ email.uid }}" class="spinner" style="display:none;">
                        <img id="img-spinner" src="{% static 'images/spinner.gif' %}" alt="Loading" height="15" />
                    </div>
                </td>
                <td style="cursor: pointer;" onclick="$(document.getElementById('{{ mailbox_name }}/{{ email.uid }}')).removeClass('bg-info');$.fancybox({href : '{% url 'email_view_message' mailbox_name=mailbox_name uid=email.uid %}', title : '{{ email.subject|escapejs }}', type: 'iframe', maxWidth: '85%', width: 1000}); $.fancybox.showLoading()">{{ email.date }}</td>
                <td style="cursor: pointer;" onclick="$(document.getElementById('{{ mailbox_name }}/{{ email.uid }}')).removeClass('bg-info');$.fancybox({href : '{% url 'email_view_message' mailbox_name=mailbox_name uid=email.uid %}', title : '{{ email.subject|escapejs }}', type: 'iframe', maxWidth: '85%', width: 1000}); $.fancybox.showLoading()">{{ email.from_name }} &lt;{{email.from_address }}&gt;</td>
                <td style="cursor: pointer;" onclick="$(document.getElementById('{{ mailbox_name }}/{{ email.uid }}')).removeClass('bg-info');$.fancybox({href : '{% url 'email_view_message' mailbox_name=mailbox_name uid=email.uid %}', title : '{{ email.subject|escapejs }}', type: 'iframe', maxWidth: '85%', width: 1000}); $.fancybox.showLoading()">{{ email.subject }}</td>
            </tr>
            {% endfor %}
        {% else %}
        <tr>
            <td colspan="4" style="text-align: center;">There are currently no emails in this mailbox.</td>
        </tr>
        {% endif %}
    """

    template = Template(raw_response)
    context = RequestContext(request, {'emails': mailbox_summary, 'mailbox_name': mailbox_name})
    response_html = template.render(context)

    data = {
        'fragments': {
            '#loading_email_record': response_html
        }
    }

    return data


@ajax
@require_POST
def email_mark_unread(request):
    post_items = request.POST.items()

    with EmailManager() as email_manager:
        for key, value in post_items:
            if key.startswith('message'):
                mailbox, uid = value.rsplit('/', 1)
                email_manager.mark_message_unread(mailbox, uid)


@ajax
@require_POST
def email_mark_read(request):
    post_items = request.POST.items()

    with EmailManager() as email_manager:
        for key, value in post_items:
            if key.startswith('message'):
                mailbox, uid = value.rsplit('/', 1)
                email_manager.mark_message_read(mailbox, uid)


@ajax
@require_POST
def email_archive(request):
    post_items = request.POST.items()
    destination_folder = request.POST['destination_folder']

    with EmailManager() as email_manager:
        for key, value in post_items:
            if key.startswith('message'):
                mailbox, uid = value.rsplit('/', 1)
                email_manager.move_message(mailbox, uid, destination_folder)


@ajax
@require_POST
def send_email(request):
    post_data = request.POST

    message = {
        'to': post_data['to'].replace(',', ';').split(';'),
        'from': 'Residence Halls Network <resnet@calpoly.edu>',
        'cc': post_data['cc'].replace(',', ';').split(';'),
        'body': post_data['body'],
        'is_html': True if post_data['is_html'] == 'true' else False,
        'subject': post_data['subject'],
        'in_reply_to': post_data.get('in_reply_to'),
    }

    with EmailManager() as email_manager:
        email_manager.send_message(message)

    return {'success': True}