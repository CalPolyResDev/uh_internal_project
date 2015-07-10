"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: ResNet Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import ssl
import imaplib, email
import datetime
import logging
import re
from ssl import SSLError, SSLEOFError
from operator import itemgetter

from django.conf import settings
from django.db import DatabaseError

from srsconnector.models import ServiceRequest

from .models import DailyDuties, VoicemailMessage
from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES
from django.core.files.base import ContentFile

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
    
    def get_voicemail(self):
        """Checks the current number of voicemail messages."""
        voicemail = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }


        def parse_message_id(messagedata):
            return messagedata.strip().split("<")[1].rstrip(">")
        def get_message_body(messagenum):
            typ, data = self.server.fetch(messagenum, 'BODY[1]')
            return data[0][1].decode()
        def get_attachment(messagenum):
            result, data = self.server.fetch(messagenum, '(RFC822)')
            m = email.message_from_string(data[0][1])
            
            if not m.get_content_maintype() == 'multipart': 
                return None
            
            for part in m.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Contnent-Disposition') is None:
                    continue

                filename = part.get_filename()
                fileData = part.get_payload(decode=True)
                return (filename, fileData)

        try:
            if not self.server:
                self._init_mail_connection()
        except (SSLError, SSLEOFError):
            voicemail["count"] = 0
            voicemail["status_color"] = RED
            voicemail["last_checked"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %H:%M%p")
            voicemail["last_user"] = "Connection Error!"
        else:
            # Select the Inbox, get the message count
            data = DailyDuties.objects.get(name='messages')
            voicemail["count"] = int(count[0])
            if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
                voicemail["status_color"] = GREEN
            else:
                voicemail["status_color"] = RED
            voicemail["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
            voicemail["last_user"] = data.last_user.get_full_name()
            
            typ, data = self.server.search(None, 'ALL')
            
            messageIDs = []
            messageNums = data[0].split()
            count = 0
            for num in messageNums:
                typ, data = self.server.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
                messageIDs[count] = parse_message_id(data)
                ++count
            
            for i in range(0, messageIDs.length - 1):
                if not VoicemailMessage.objects.filter(imap_uuid = messageIDs[i]).exists():
                    msgText = get_message_body(messageNums[i])
                    dateString = msgText[27:41]
                    fromIdx = msgText.find('from')
                    fromString = msgText[fromIdx+5:msgText.find('.', fromIdx)]
                    date = datetime.datetime.strptime(dateString, "%H:%M %m-%d-%y")
                    
                    attachment = get_attachment(messageNums[i])
                    if attachment == None: #Invalid Voicemail Email
                        continue
                    aFile = ContentFile(attachment[1])

                    newMsg = VoicemailMessage(imap_uuid=messageIDs[i], sender=fromString, date=date)
                    newMsg.attachment.save(attachment[0], aFile)
                    newMsg.save()

        return voicemail

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
