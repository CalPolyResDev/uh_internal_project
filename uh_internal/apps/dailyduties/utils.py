"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: University Housing Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""
from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.db import DatabaseError
from srsconnector.utils import get_ticket_count

# https://github.com/fedorareis/pyexchange This is a combination of branches with some custom code
from pyexchange import Exchange2010Service, ExchangeBasicAuthConnection
from pyexchange.exceptions import FailedExchangeException

from .models import DailyDuties

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = timedelta(days=1)


class GetInboxCount(object):
    """Utility for gathering count of emails and voicemails in inbox"""

    @staticmethod
    def setup():
        """ Creates the Exchange Connection """
        # Set up the connection to Exchange
        connection = ExchangeBasicAuthConnection(url=settings.OUTLOOK_URL,
                                                 username=settings.EMAIL_USERNAME,
                                                 password=settings.EMAIL_PASSWORD)

        service = Exchange2010Service(connection)

        return service

    @staticmethod
    def get_mail_count(service):
        """ Returns the number of emails in the Inbox """

        folder = service.folder()
        folder_id = "inbox"
        email = folder.get_folder(folder_id)

        return email.total_count

    @staticmethod
    def get_voicemail_count(service):
        """ Returns the number of emails in the Voicemail Folder """

        folder = service.folder()
        voicemail = folder.get_folder(settings.OUTLOOK_VOICEMAIL_FOLDER_ID)

        return voicemail.total_count


class GetDutyData(object):
    """ Utility for gathering daily duty data."""

    def get_voicemail(self, server):
        """Checks the current number of voicemail messages."""

        voicemail = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        data = DailyDuties.objects.get(name='voicemail')

        try:
            count = GetInboxCount.get_voicemail_count(server)
            voicemail["count"] = count
        except FailedExchangeException:
            voicemail["count"] = '?'

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

        # fetch email with pyexchange
        try:
            count = GetInboxCount.get_mail_count(server)
            email["count"] = count
        except FailedExchangeException:
            email["count"] = '?'

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
            data = DailyDuties.objects.get(name='tickets')

            tickets["count"] = get_ticket_count(full_name=str(user.get_full_name()))
            if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
                tickets["status_color"] = GREEN
            else:
                tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
            tickets["last_user"] = data.last_user.get_full_name()
        except DatabaseError as message:
            logger.exception(message, exc_info=True)
            tickets["count"] = '?'
            tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            tickets["last_user"] = "Connection Error!"

        return tickets
