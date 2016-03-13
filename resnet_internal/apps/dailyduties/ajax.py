"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: University Housing Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import datetime
from operator import itemgetter
from urllib.parse import unquote
import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.template import Template, RequestContext
from django.utils.encoding import smart_text
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax
from jfu.http import upload_receive, UploadResponse, JFUResponse

from ..core.models import Building
from ..core.templatetags.srs_urls import srs_edit_url
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
            '#ticket_manager_text': duty_dict_to_link_text(duty_data['tickets'], 'Ticket Manager'),
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


@cache_page(60 * 60 * 24)
def get_email_folders(request):
    with EmailManager() as email_manager:
        folder_response = email_manager.server.list_folders()

    folder_response.sort(key=itemgetter(2))

    html_response = "<ul><li class='jstree-open' id='root'>ResNet Email<ul>"
    current_parents = []
    hide_list = ('Journal', 'Notes', 'Tasks', 'Voicemails',
                 'Archive', 'Clutter', 'Drafts', 'Outbox')

    for flags, delimiter, folder_name in folder_response:

        hierarchical_list = folder_name.split(smart_text(delimiter))

        if current_parents and (len(hierarchical_list) < 2 or not current_parents[-1] == hierarchical_list[-2]):
            html_response += '</li></ul>'
            current_parents.pop()

        if folder_name in hide_list:
            continue

        if folder_name.startswith(('Calendar', 'Contacts', 'Deleted Items')):
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
def get_mailbox_summary(request, **kwargs):
    mailbox_name = unquote(kwargs["mailbox_name"])
    search_string = unquote(kwargs["search_string"])

    MESSAGES_PER_GROUP = 100
    message_group = kwargs.get('message_group')
    message_range = [int(message_group) * MESSAGES_PER_GROUP, (int(message_group) + 1) * MESSAGES_PER_GROUP - 1] if message_group and int(message_group) is not None else None

    if mailbox_name and mailbox_name == 'root':
        messages = None
        num_available_messages = 0
    else:
        with EmailManager() as email_manager:
            (messages, num_available_messages) = email_manager.get_messages(mailbox_name, search_string, range=message_range)

    for email in messages:
        email['full_id'] = email['mailbox'] + '/' + str(email['uid'])
        email['modal_title'] = 'Email'

    if message_range and num_available_messages > 0:
        if message_range[1] + 2 > num_available_messages:
            next_group_url = None
        else:
            next_group_url = reverse('dailyduties:email_get_mailbox_summary_range', kwargs={'mailbox_name': mailbox_name, 'search_string': search_string, 'message_group': str(int(message_group) + 1)})
    else:
        next_group_url = None

    raw_response = """
        {% load staticfiles %}
        {% if emails %}
            {% for email in emails %}
            <tr id="{{ email.full_id }}" {% if email.unread %}class="bg-info"{% endif %}>
                <td>
                    <input type="checkbox" name="email_selection" value="{{ email.uid }}" id="checkbox_{{ email.full_id }}">
                    <div id="spinner_{{ email.full_id }}" class="spinner" style="display:none;">
                        <img id="img-spinner" src="{% static 'images/spinner.gif' %}" alt="Loading" height="15" />
                    </div>
                </td>
                <td>
                    {% if email.replied %}
                        <img src="{% static 'images/mail_reply.png' %}"></img>
                    {% endif %}
                </td>
                <td style="cursor: pointer;" onclick="$(document.getElementById('{{ email.full_id }}')).removeClass('bg-info');openModalFrame('{{ email.modal_title|escapejs }}', '{% url 'email_view_message' mailbox_name=email.mailbox uid=email.uid %}');">{{ email.date }}</td>
                <td style="cursor: pointer;" onclick="$(document.getElementById('{{ email.full_id }}')).removeClass('bg-info');openModalFrame('{{ email.modal_title|escapejs }}', '{% url 'email_view_message' mailbox_name=email.mailbox uid=email.uid %}');">{{ email.sender_name }} &lt;{{email.sender_address }}&gt;</td>
                <td style="cursor: pointer;" onclick="$(document.getElementById('{{ email.full_id }}')).removeClass('bg-info');openModalFrame('{{ email.modal_title|escapejs }}', '{% url 'email_view_message' mailbox_name=email.mailbox uid=email.uid %}');">{{ email.subject }}</td>
                {% if mailbox_name|length == 0 %}
                    <td style="cursor: pointer;" onclick="$(document.getElementById('{{ email.full_id }}')).removeClass('bg-info');openModalFrame('{{ email.modal_title|escapejs }}', '{% url 'dailyduties:email_view_message' mailbox_name=email.mailbox uid=email.uid %}');">{{ email.mailbox }}</td>
                {% endif %}
            </tr>
            {% endfor %}
        {% else %}
        <tr>
            <td colspan="100" style="text-align: center;">
                {% if is_search %}
                    There are no messages matching '{{ search_string|escape }}'.
                {% else %}
                    There are currently no emails in this mailbox.
                {% endif %}
            </td>
        </tr>
        {% endif %}
    """

    template = Template(raw_response)
    context = RequestContext(request, {'emails': messages,
                                       'mailbox_name': mailbox_name,
                                       'is_search': bool(search_string),
                                       'search_string': search_string,
                                       'next_group_url': next_group_url,
                                       })
    response_html = template.render(context)

    return {'html': response_html, 'next_group_url': (next_group_url if next_group_url else '')}


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

    attachments = []
    for key, value in post_data.items():
        if key.startswith('attachment'):
            attachment = cache.get(value)
            if not attachment:
                return {'success': False, 'reason': 'Could not retrieve attachments. Please re-attach and try again.'}
            attachments.append(attachment)

    message = {
        'to': post_data['to'].replace(',', ';').split(';'),
        'from': 'Residence Halls Network <resnet@calpoly.edu>',
        'cc': post_data['cc'].replace(',', ';').split(';'),
        'body': post_data['body'],
        'is_html': True if post_data['is_html'] == 'true' else False,
        'subject': post_data['subject'],
        'in_reply_to': post_data.get('in_reply_to'),
        'attachments': attachments,
    }

    with EmailManager() as email_manager:
        email_manager.send_message(message)

    return {'success': True}


@require_POST
def attachment_upload(request, **kwargs):

    # The assumption here is that jQuery File Upload
    # has been configured to send files one at a time.
    # If multiple files can be uploaded simulatenously,
    # 'file' may be a list of files.
    file = upload_receive(request)

    cache_key = 'email_attachment:' + request.user.username + str(datetime.utcnow()) + ':' + file.name
    cache.set(cache_key, file, 24 * 60 * 60)

    file_dict = {
        'name': file.name,
        'size': file.size,
        'cacheKey': cache_key,
        'deleteUrl': reverse('dailyduties:jfu_delete', kwargs={'pk': cache_key}),
        'deleteType': 'POST',
    }

    return UploadResponse(request, file_dict)


@require_POST
def attachment_delete(request, pk):
    success = True
    try:
        cache.delete(pk)
    except:
        success = False

    return JFUResponse(request, success)


@ajax
@require_POST
def ticket_from_email(request):
    post_items = request.POST

    [mailbox_name, uid] = post_items['message_path'].rsplit('/', 1)
    user_full_name = request.user.get_full_name()

    with EmailManager() as email_manager:
        ticket_number = email_manager.create_ticket_from_email(mailbox_name, uid, post_items['requestor_username'], user_full_name)

    return {'redirect_url': srs_edit_url(ticket_number)}


@ajax
@require_POST
def get_csd_email(request):
    success = True

    try:
        csd_mappings = Building.objects.get(id=request.POST['building_id']).csdmappings
        csd_emails = ['%s <%s>' % (mapping.name, mapping.email) for mapping in csd_mappings.all()]
        csd_email_string = ', '.join(csd_emails)
    except Building.DoesNotExist:
        success = False
        csd_email_string = ''

    response = {
        'email_string': csd_email_string,
        'success': success
    }

    return response
