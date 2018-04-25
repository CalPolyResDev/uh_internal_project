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
from django.http.response import HttpResponse
from django.template import Template, RequestContext
from django.urls import reverse
from django.utils.encoding import smart_text
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django_datatables_view.mixins import JSONResponseView
from jfu.http import upload_receive, UploadResponse, JFUResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..core.models import Building
from ..core.templatetags.srs_urls import srs_edit_url
from .models import DailyDuties
from .utils import GetInboxCount, GetDutyData

logger = logging.getLogger(__name__)


@api_view(['GET'])
def refresh_duties(request):
    duty_data = cache.get('duty_data')

    server = GetInboxCount.setup()

    if not duty_data:
        duty_data_manager = GetDutyData()

        duty_data = {
            'voicemail': duty_data_manager.get_voicemail(server),
            'email': duty_data_manager.get_email(server),
            'tickets': duty_data_manager.get_tickets(request.user),
        }
        cache.set('duty_data', duty_data, 120)

    def duty_dict_to_link_text(daily_duty_dict, name):
        return_string = name
        if daily_duty_dict['count'] == '?':
            return_string += ' <strong class="text-warning">(' + daily_duty_dict['count'] + ')</strong>'
        elif daily_duty_dict['count'] > 10:
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
            '#voicemail_text': duty_dict_to_link_text(duty_data['voicemail'], 'Voicemail'),
            '#email_text': duty_dict_to_link_text(duty_data['email'], 'Email'),
            '#ticket_manager_text': duty_dict_to_link_text(duty_data['tickets'], 'Ticket Manager'),
        },
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
