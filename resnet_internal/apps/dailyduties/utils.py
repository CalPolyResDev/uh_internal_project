"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: ResNet Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""
import imaplib
import email
from datetime import datetime, timedelta
import logging
from ssl import SSLError, SSLEOFError

from django.conf import settings
from django.db import DatabaseError

from srsconnector.models import ServiceRequest

from .models import DailyDuties
from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES
from django.core.files.base import ContentFile
from email.parser import HeaderParser
from email.utils import parseaddr

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = timedelta(days=1)


class EmailConnectionMixin(object):

    def _init_mail_connection(self):
        # Connect to the email server and authenticate
        if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
            self.server = imaplib.IMAP4_SSL(host=settings.INCOMING_EMAIL['IMAP4']['HOST'], port=settings.INCOMING_EMAIL['IMAP4']['PORT'])
        else:
            self.server = imaplib.IMAP4(host=settings.INCOMING_EMAIL['IMAP4']['HOST'], port=settings.INCOMING_EMAIL['IMAP4']['PORT'])
        self.server.login(user=settings.INCOMING_EMAIL['IMAP4']['USER'], password=settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])


class VoicemailManager(EmailConnectionMixin):
    server = None
    
    def parse_message_id(self, messagedata):
        hp = HeaderParser()
        header_string = str(messagedata[0][1])
        message_id = header_string.split('<')[1].rsplit('>')[0]
        return message_id

    def get_message_body(self, messagenum):
        data = self.server.fetch(messagenum, 'BODY[1]')[1]
        return data[0][1].decode()

    def get_message_nums(self):
        data = self.server.search(None, 'ALL')[1]
        return data[0].split()

    def get_message_uuids(self, messageNums):
        messageIDs = []
        count = 0
        for num in messageNums:
            data = self.server.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')[1]
            messageIDs.append(self.parse_message_id(data))
            ++count
        return (count, messageIDs)

    def get_messagenum_for_uuid(self, uuid):
        messageNums = self.get_message_nums()
        messageUUIDs = self.get_message_uuids(messageNums)[1]

        messageNum = None
        for i in range(0, len(messageUUIDs) - 1):
            if messageUUIDs[i] == uuid:
                messageNum = messageNums[i]
                break
        return messageNum

    def get_attachment(self, messagenum):
        data = self.server.fetch(messagenum, '(RFC822)')
        print(str(data[1][0][1]))
        voicemail_message = email.message_from_string(str(data[1][0][1]))

        for part in voicemail_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            fileData = part.get_payload(decode=True)
            
            print(fileData)
            return (filename, ContentFile(fileData))
        
        raise ValueError('Not a Valid Voicemail Message: No attachment.')

    def get_attachment_uuid(self, messageuuid):
        if self.server is None:
            self._init_mail_connection()
        self.server.select('Voicemails', readonly=True)

        messageNum = self.get_messagenum_for_uuid(messageuuid)
        print(messageNum)

        if messageNum is None:
            raise ValueError('Unable to retrieve voicemail message attachment because message uuid could not be found.')

        return self.get_attachment(messageNum)

    def delete_message(self, messageUUID):
        if self.server is None:
            self._init_mail_connection()
        self.server.select('Voicemails', readonly=False)

        messageNum = self.get_messagenum_for_uuid(messageUUID)
        result = self.server.copy(messageNum, 'Archives/Voicemails')
        if (result == 'OK'):
            self.server.store(messageNum, '+FLAGS', '\\Deleted')
            self.server.expunge()

    def get_all_voicemail(self):
        """Get the voicemail messages."""
        voicemail = []
        
        try:
            if not self.server:
                self._init_mail_connection()

        except (SSLError, SSLEOFError):
            voicemail = [{"date": datetime.time(), "sender": "Connection Error", "uuid": "Error!"}]
        else:
            # Select the Voicemail Mailbox, get the message count
            self.server.select('Voicemails', readonly=True)

            message_nums = self.get_message_nums()
            message_ids = self.get_message_uuids(message_nums)[1]

            for i in range(0, len(message_ids) - 1):
                msg_text = self.get_message_body(message_nums[i])
                date_string = msg_text[27:41]
                from_idx = msg_text.find('from')
                from_string = msg_text[from_idx + 5:msg_text.find('.', from_idx)]
                date = datetime.strptime(date_string, "%H:%M %m-%d-%y")

                new_msg = {
                    "date": date,
                    "sender": from_string,
                    "uuid": message_ids[i],
                    "url": "daily_duties/voicemail/" + message_ids[i]
                }

                voicemail.append(new_msg)
        
        return voicemail


class GetDutyData(EmailConnectionMixin):
    """ Utility for gathering daily duty data."""

    server = None

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
            voicemail["last_checked"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            voicemail["last_user"] = "Connection Error!"
        else:
            data = DailyDuties.objects.get(name='messages')

            count = self.server.select('Voicemails', readonly=True)[1]
            self.server.logout()

            # Select the Inbox, get the message count
            voicemail["count"] = int(count[0])
            if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
                voicemail["status_color"] = GREEN
            else:
                voicemail["status_color"] = RED
            voicemail["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
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
            email["last_checked"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            email["last_user"] = "Connection Error!"
        else:
            data = DailyDuties.objects.get(name='email')

            # Select the Inbox, get the message count
            count = self.server.select('Inbox', readonly=True)[1]
            self.server.logout()

            email["count"] = int(count[0])
            if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
                email["status_color"] = GREEN
            else:
                email["status_color"] = RED
            email["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
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
            if data.last_checked > datetime.now() - ACCEPTABLE_LAST_CHECKED:
                tickets["status_color"] = GREEN
            else:
                tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(data.last_checked, "%Y-%m-%d %H:%M")
            tickets["last_user"] = data.last_user.get_full_name()
        except DatabaseError as message:
            logger.exception(message)
            tickets["count"] = 0
            tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            tickets["last_user"] = "Connection Error!"

        return tickets
