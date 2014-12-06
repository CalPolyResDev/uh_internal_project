"""
.. module:: resnet_internal.apps.core.utils
   :synopsis: ResNet Internal Core Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import ssl
import imaplib
import datetime
import logging
from copy import deepcopy

from django.conf import settings
from django.db import DatabaseError

from srsconnector.models import ServiceRequest

from .models import DailyDuties
from ssl import SSLError, SSLEOFError

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = datetime.timedelta(days=1)


def dict_merge(base, merge):
    """ Recursively merges dictionaries.

    :param base: The base dictionary.
    :type base: dict
    :param merge: The dictionary to merge with base.
    :type merge: dict

    """

    if not isinstance(merge, dict):
        return merge
    result = deepcopy(base)

    for key, value in merge.items():
        if key in result and isinstance(result[key], dict):
                result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


class GetDutyData(object):
    """ Utility for gathering daily duty data."""

    server = None

    def _init_mail_connection(self):
        # Connect to the email server and authenticate
        if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.set_ciphers("RC4-MD5")
            self.server = imaplib.IMAP4_SSL(host=settings.INCOMING_EMAIL['IMAP4']['HOST'], port=settings.INCOMING_EMAIL['IMAP4']['PORT'], ssl_context=context)
        else:
            self.server = imaplib.IMAP4(host=settings.INCOMING_EMAIL['IMAP4']['HOST'], port=settings.INCOMING_EMAIL['IMAP4']['PORT'])
        self.server.login(user=settings.INCOMING_EMAIL['IMAP4']['USER'], password=settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])

    def get_messages(self):
        """Checks the current number of voicemail messages."""

        messages = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        data = DailyDuties.objects.get(name='messages')

        messages["count"] = 0
        if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
            messages["status_color"] = GREEN
        else:
            messages["status_color"] = RED
        messages["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
        messages["last_user"] = data.last_user.get_full_name()

        return messages

    def get_email(self):
        """Checks the current number of unread email messages."""

        email = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        try:
            self._init_mail_connection()
        except (SSLError, SSLEOFError):
            email["count"] = 0
            email["status_color"] = RED
            email["last_checked"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %H:%M%p")
            email["last_user"] = "Connection Error!"
        else:
            # Grab the number of unread emails
            r, count = self.server.select('inbox', readonly=True)  # Select the Inbox, grab the count
            self.server.logout()  # Disconnect from the email server

            data = DailyDuties.objects.get(name='email')

            email["count"] = int(count[0])
            if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
                email["status_color"] = GREEN
            else:
                email["status_color"] = RED
            email["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
            email["last_user"] = data.last_user.get_full_name()

        return email

    def get_tickets(self):
        """Checks the current number of queued SRS tickets."""

        tickets = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        try:
            open_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET").exclude(status=4).count()
            api_tickets = ServiceRequest.objects.filter(assigned_person="ResnetAPI").count()

            data = DailyDuties.objects.get(name='tickets')

            tickets["count"] = open_tickets - api_tickets
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
