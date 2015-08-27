"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: ResNet Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""
import email
from datetime import datetime, timedelta
import logging
from ssl import SSLError, SSLEOFError
from operator import itemgetter

from django.conf import settings
from django.db import DatabaseError
from django.utils.encoding import smart_text

import imapclient

from srsconnector.models import ServiceRequest

from .models import DailyDuties
from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = timedelta(days=1)


class EmailConnectionMixin(object):

    def __init__(self, *args, **kwargs):
        super(EmailConnectionMixin, self).__init__(*args, **kwargs)
        if self.server is None:
            self._init_mail_connection()

    def __enter__(self):
        if self.server is None:
            self._init_mail_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.server.logout()

    def _init_mail_connection(self):
        host = settings.INCOMING_EMAIL['IMAP4']['HOST']
        port = settings.INCOMING_EMAIL['IMAP4']['PORT']
        username = settings.INCOMING_EMAIL['IMAP4']['USER']
        password = settings.INCOMING_EMAIL['IMAP4']['PASSWORD']
        ssl = settings.INCOMING_EMAIL['IMAP4']['USE_SSL']
        self.server = imapclient.IMAPClient(host, port=port, use_uid=True, ssl=ssl)
        self.server.login(username, password)


class EmailManager(EmailConnectionMixin):
    server = None

    def get_attachment(self, uid):
        response = self.server.fetch(int(uid), 'BODY[]')

        message = email.message_from_bytes(response[int(uid)][b'BODY[]'])

        for part in message.walk():

            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            file_data = part.get_payload(decode=True)

            return (filename, file_data)

        raise ValueError('Not a Valid Voicemail Message: No attachment.')

    def delete_voicemail_message(self, uid):
        self.server.select_folder('Voicemails')

        try:
            self.server.copy(int(uid), 'Archives/Voicemails')
        except:
            print('Copy Failed!')
            return

        self.server.delete_messages(int(uid))
        self.server.expunge()

    def get_all_voicemail_messages(self):
        """Get the voicemail messages."""
        voicemails = []

        self.server.select_folder('Voicemails', readonly=True)
        uids = self.server.search()

        # Check for empty inbox
        if not uids:
            return None

        response = self.server.fetch(uids, ['BODY[1]'])

        for uid, data in response.items():
            body = smart_text(data[b'BODY[1]'])

            date_string = body[27:41]

            from_idx = body.find('from')
            from_string = body[from_idx + 5:body.find('.', from_idx)]

            date = datetime.strftime(datetime.strptime(date_string, "%H:%M %m-%d-%y"), "%Y-%m-%d %H:%M")

            message = {
                "date": date,
                "sender": from_string,
                "message_uid": uid,
                "url": "daily_duties/voicemail/" + str(uid)
            }
            voicemails.append(message)

        voicemails.sort(key=itemgetter('date'), reverse=True)
        return voicemails

    def get_mailbox_summary(self, mailbox_name):
        self.server.select_folder(mailbox_name)
        message_uids = self.server.search()
        response = self.server.fetch(message_uids, ['ALL'])

        messages = []
        for uid, data in response.items():
            unread = b'\\Seen' not in data[b'FLAGS']
            envelope = data[b'ENVELOPE']
            date = envelope.date
            subject = envelope.subject
            message_from = envelope.from_[0]

            messages.append({
                'uid': uid,
                'unread': unread,
                'date': date,
                'subject': smart_text(subject),
                'from_name': smart_text(message_from.name),
                'from_address': smart_text(message_from.mailbox) + '@' + smart_text(message_from.host)
            })

        return messages


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

            count = self.server.select_folder('Voicemails', readonly=True)[b'EXISTS']

            # Select the Inbox, get the message count
            voicemail["count"] = count
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
            count = self.server.select_folder('Inbox', readonly=True)[b'EXISTS']

            email["count"] = count
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
