"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: ResNet Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import ssl
import imaplib
import datetime
import logging
from ssl import SSLError, SSLEOFError

from django.conf import settings
from django.db import DatabaseError

from srsconnector.models import ServiceRequest

from .models import DailyDuties
from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = datetime.timedelta(days=1)


class GetDutyData(object):
    """ Utility for gathering daily duty data."""

    server = None

    def _init_mail_connection(self):
        # Connect to the email server and authenticate
        if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
            self.server = imaplib.IMAP4_SSL(host=settings.INCOMING_EMAIL['IMAP4']['HOST'], port=settings.INCOMING_EMAIL['IMAP4']['PORT'])
        else:
            self.server = imaplib.IMAP4(host=settings.INCOMING_EMAIL['IMAP4']['HOST'], port=settings.INCOMING_EMAIL['IMAP4']['PORT'])
        self.server.login(user=settings.INCOMING_EMAIL['IMAP4']['USER'], password=settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])

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
        if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
            printer_requests["status_color"] = GREEN
        else:
            printer_requests["status_color"] = RED
        printer_requests["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
        printer_requests["last_user"] = data.last_user.get_full_name()

        return printer_requests

    def get_messages(self):
        """Checks the current number of voicemail messages."""

        voicemail = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        try:
            if not self.server:
                self._init_mail_connection()
        except (SSLError, SSLEOFError):
            voicemail["count"] = 0
            voicemail["status_color"] = RED
            voicemail["last_checked"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %H:%M%p")
            voicemail["last_user"] = "Connection Error!"
        else:
            data = DailyDuties.objects.get(name='messages')

            r, count = self.server.select('Voicemails', readonly=True)
            self.server.logout()

            # Select the Inbox, get the message count
            voicemail["count"] = int(count[0])
            if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
                voicemail["status_color"] = GREEN
            else:
                voicemail["status_color"] = RED
            voicemail["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
            voicemail["last_user"] = data.last_user.get_full_name()

        return voicemail

    def get_email(self):
        """Checks the current number of unread email messages."""

        email = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        try:
            if not self.server:
                self._init_mail_connection()
        except (SSLError, SSLEOFError):
            email["count"] = 0
            email["status_color"] = RED
            email["last_checked"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %H:%M%p")
            email["last_user"] = "Connection Error!"
        else:
            data = DailyDuties.objects.get(name='email')

            # Select the Inbox, get the message count
            r, count = self.server.select('Inbox', readonly=True)
            self.server.logout()

            email["count"] = int(count[0])
            if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
                email["status_color"] = GREEN
            else:
                email["status_color"] = RED
            email["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
            email["last_user"] = data.last_user.get_full_name()

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
            if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
                tickets["status_color"] = GREEN
            else:
                tickets["status_color"] = RED
            tickets["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
            tickets["last_user"] = data.last_user.get_full_name()
        except DatabaseError as message:
            logger.exception(message)
            tickets["count"] = 0
            tickets["status_color"] = RED
            tickets["last_checked"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %H:%M%p")
            tickets["last_user"] = "Connection Error!"

        return tickets
