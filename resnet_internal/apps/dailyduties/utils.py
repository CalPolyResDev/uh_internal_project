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
from operator import itemgetter

from django.conf import settings
from django.db import DatabaseError

from srsconnector.models import ServiceRequest

from .models import DailyDuties
from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES

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
    
    def __init__(self, *args, **kwargs):
        super(VoicemailManager, self).__init__(*args, **kwargs)
        if self.server is None:
            self._init_mail_connection()
    
    def __enter__(self):
        if self.server is None:
            self._init_mail_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.server.logout()
    
    def _parse_message_id(self, message_id_string):
        return message_id_string.split('<')[1].rsplit('>')[0]

    def _get_message_body(self, message_number):
        data = self.server.fetch(message_number, 'BODY[1]')[1]
        return data[0][1].decode()
    
    def _build_message_set(self, message_numbers):
        message_set_string = ''
        for message_number in message_numbers:
            message_set_string = message_set_string + ',' + message_number.decode('utf_8')
        
        message_set_string = message_set_string.split(',', 1)[-1]
        message_set = bytes(message_set_string, 'utf-8')
        
        return message_set if message_set else None
    
    def _get_message_set_length(self, message_set):
        return len(message_set.decode('utf-8').split(','))
    
    def _get_message_bodies(self, message_set):
        data = self.server.fetch(message_set, 'BODY[1]')[1]
        
        message_bodies = []
        for message_index in range(0, self._get_message_set_length(message_set)):
            message_bodies.append(data[message_index * 2][1].decode('utf-8'))
        
        return message_bodies

    def _get_message_numbers(self):
        data = self.server.search(None, 'ALL')[1]
        return data[0].split()

    def _get_message_uuids(self, message_set):
        data = self.server.fetch(message_set, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')[1]
        message_uuids = []
        
        for message_index in range(0, self._get_message_set_length(message_set)):
            message_uuids.append(self._parse_message_id(data[message_index * 2][1].decode('utf-8')))
            
        return message_uuids

    def _get_messagenum_for_uuid(self, message_uuid):
        message_numbers = self._get_message_numbers()
        message_uuids = self._get_message_uuids(self._build_message_set(message_numbers))

        message_number = None
        
        if message_uuid in message_uuids:
            message_number = message_numbers[message_uuids.index(message_uuid)]
        
        return message_number

    def _get_attachment_by_message_number(self, message_number):
        data = self.server.fetch(message_number, '(RFC822)')
        voicemail_message = email.message_from_bytes(data[1][0][1])
        
        for part in voicemail_message.walk():
            
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            file_data = part.get_payload(decode=True)

            return (filename, file_data)
        
        raise ValueError('Not a Valid Voicemail Message: No attachment.')

    def get_attachment_by_uuid(self, message_uuid):
        self.server.select('Voicemails', readonly=True)

        message_number = self._get_messagenum_for_uuid(message_uuid)

        if not message_number:
            raise ValueError('Unable to retrieve voicemail message attachment because message uuid could not be found.')

        return self._get_attachment_by_message_number(message_number)

    def delete_message(self, message_uuid):
        self.server.select('Voicemails', readonly=False)

        message_number = self._get_messagenum_for_uuid(message_uuid)
        
        imap_query_result = self.server.copy(message_number, 'Archives/Voicemails')
        if (imap_query_result[0] == 'OK'):
            self.server.store(message_number, '+FLAGS', '\\Deleted')
            self.server.expunge()
        else:
            print('Copy Failed: ' + str(imap_query_result))

    def get_all_voicemail_messages(self):
        """Get the voicemail messages."""
        voicemails = []

        self.server.select('Voicemails', readonly=True)
        message_numbers = self._get_message_numbers()
        
        # Check for empty inbox
        if not message_numbers:
            return None
        
        message_uuids = self._get_message_uuids(self._build_message_set(message_numbers))
        message_bodies = self._get_message_bodies(self._build_message_set(message_numbers))

        for message_uuid, message_body in zip(message_uuids, message_bodies):
            date_string = message_body[27:41]
            
            from_idx = message_body.find('from')
            from_string = message_body[from_idx + 5:message_body.find('.', from_idx)]
            
            date = datetime.strftime(datetime.strptime(date_string, "%H:%M %m-%d-%y"), "%Y-%m-%d %H:%M")

            message = {
                "date": date,
                "sender": from_string,
                "message_uuid": message_uuid,
                "url": "daily_duties/voicemail/" + message_uuid
            }

            voicemails.append(message)
        
        voicemails.sort(key=itemgetter('date'), reverse=True)
        return voicemails


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
