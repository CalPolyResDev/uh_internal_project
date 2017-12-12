"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: University Housing Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_datatables_view.mixins import JSONResponseView
from jfu.http import upload_receive, UploadResponse, JFUResponse

from ..core.models import Building
from ..core.templatetags.srs_urls import srs_edit_url
from .models import DailyDuties, EmailViewingRecord
from .utils import GetDutyData
from .authhelper import get_token, get_admin_consent

logger = logging.getLogger(__name__)


@api_view(['GET'])
def refresh_duties(request):
    duty_data = cache.get('duty_data')
    admin_consent = get_admin_consent()
    # token = get_token()
    token = 1

    if not duty_data:
        duty_data_manager = GetDutyData()
        # api_request = duty_data_manager.send_api_request(token)

        duty_data = {
            'printer_requests': duty_data_manager.get_printer_requests(),
            'voicemail': duty_data_manager.get_voicemail(token),
            'email': duty_data_manager.get_email(token),
            'tickets': duty_data_manager.get_tickets(request.user),
        }
        cache.set('duty_data', duty_data, 120)

    def duty_dict_to_link_text(daily_duty_dict, name):
        return_string = name
        print(daily_duty_dict['count'])
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

    return Response(data)


@api_view(['POST'])
def update_duty(request):
    """ Update a particular duty.

    :param duty: The duty to update.
    :type duty: str

    """

    # Pull post parameters
    duty = request.data["duty"]

    data = DailyDuties.objects.get(name=duty)
    data.last_checked = datetime.now()
    data.last_user = get_user_model().objects.get(username=request.user.username)
    data.save()

    return Response()
