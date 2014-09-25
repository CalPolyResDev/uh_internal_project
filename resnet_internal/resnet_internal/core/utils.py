"""
.. module:: resnet_internal.core.utils
   :synopsis: ResNet Internal Core Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import datetime
import imaplib
import logging
from copy import deepcopy

from django.conf import settings
from django.db import DatabaseError

from srsconnector.models import ServiceRequest

from .models import DailyDuties

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

    for key, value in merge.iteritems():
        if key in result and isinstance(result[key], dict):
                result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


class GetDutyData(object):
    """ Utility for gathering daily duty data."""

    def get_messages(self):
        """Checks the current number of voicemail messages.

        An API for this has not been discovered yet; For now this method always returns zero.

        """

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
        server = None

        # Connect to the email server and authenticate
        if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
            server = imaplib.IMAP4_SSL(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
        else:
            server = imaplib.IMAP4(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
        server.login(settings.INCOMING_EMAIL['IMAP4']['USER'], settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])

        # Grab the number of unread emails
        server.select('inbox', readonly=True)  # Select the Inbox
        r, search_data = server.search(None, "UnSeen")  # Search for unread emails
        unread_count = len(search_data[0].split())  # Count unread emails
        server.logout()  # Disconnect from the email server

        data = DailyDuties.objects.get(name='email')

        email["count"] = unread_count
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
        except DatabaseError, message:
            logger.info(message)
            tickets["count"] = 0
            tickets["status_color"] = RED
            tickets["last_checked"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %H:%M%p")
            tickets["last_user"] = "Connection Error!"

        return tickets