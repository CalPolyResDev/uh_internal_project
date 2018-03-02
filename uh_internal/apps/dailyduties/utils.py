"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: University Housing Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from itertools import zip_longest
import itertools
import logging
from operator import itemgetter
import os
import socket
from ssl import SSLError, SSLEOFError
from threading import Lock
import requests

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.db import DatabaseError
from django.utils.encoding import smart_text
from srsconnector.models import ServiceRequest

from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES
from .models import DailyDuties
from .pyexchange import get_mail, get_voicemail, setup

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = timedelta(days=1)

ms_api_url = "https://graph.microsoft.com/v1.0/users"

class GetDutyData(object):
    """ Utility for gathering daily duty data."""

    def get_printer_requests(self):
        """Checks the current number of printer requests."""

        printer_requests = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        data = DailyDuties.objects.get(name='printerrequests')

        printer_requests["count"] = PrinterRequest.objects.filter(status=REQUEST_STATUSES.index("Open")).count()
        if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
            printer_requests["status_color"] = GREEN
        else:
            printer_requests["status_color"] = RED
        printer_requests["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
        printer_requests["last_user"] = data.last_user.get_full_name()

        return printer_requests

    def get_voicemail(self, server):
        """Checks the current number of voicemail messages."""

        voicemail = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        data = DailyDuties.objects.get(name='voicemail')

        count = get_voicemail(server)
        voicemail["count"] = count

        if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
            voicemail["status_color"] = GREEN
        else:
            voicemail["status_color"] = RED
        voicemail["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
        voicemail["last_user"] = data.last_user.get_full_name()

        return voicemail

    def get_email(self, server):
        """Checks the current number of unread email messages."""

        email = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        data = DailyDuties.objects.get(name='email')

        #fetch email with pyexchange
        count = get_mail(server)
        email["count"] = count

        if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
            email["status_color"] = GREEN
        else:
            email["status_color"] = RED
        email["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
        email["last_user"] = data.last_user.get_full_name() if data.last_user else '[Deleted User]'

        return email

    def get_tickets(self, user):
        """Checks the current number of queued SRS tickets."""

        tickets = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        try:
            # If ORs were possible with SRS, this would be a lot cleaner...
            total_open_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET").exclude(status=4).exclude(status=8).count()
            assigned_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET").exclude(status=4).exclude(status=8).exclude(assigned_person="").count()
            my_assigned_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET", assigned_person=str(user.get_full_name())).exclude(status=4).exclude(status=8).count()

            data = DailyDuties.objects.get(name='tickets')

            tickets["count"] = (total_open_tickets - assigned_tickets) + my_assigned_tickets
            if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
                tickets["status_color"] = GREEN
            else:
                tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
            tickets["last_user"] = data.last_user.get_full_name()
        except DatabaseError as message:
            logger.exception(message, exc_info=True)
            tickets["count"] = 0
            tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            tickets["last_user"] = "Connection Error!"

        return tickets

    def send_api_request(self, token):
        api_data = {
            'Authorization' : 'Bearer ' + token
        }

        r = requests.get(ms_api_url, data=api_data)
        try:
            print(r.text)
            return r.json()
        except:
            'Error sending API request: {0} - {1}'.format(r.status_code, r.text)
