"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: ResNet Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""
from datetime import datetime, timedelta
from email import header
from itertools import zip_longest
from operator import itemgetter
from ssl import SSLError, SSLEOFError
import email
import imapclient
import logging

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.core.mail.message import EmailMessage
from django.db import DatabaseError
from django.utils.encoding import smart_text

from srsconnector.models import ServiceRequest

from ..printerrequests.models import Request as PrinterRequest, REQUEST_STATUSES
from .models import DailyDuties


imapclient.imapclient.imaplib._MAXLINE = 1000000

logger = logging.getLogger(__name__)

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = timedelta(days=1)


def get_archive_folders():
    archive_folders = [
        ('Archives/Aruba Ethernet', 'Aruba Ethernet'),
        ('Archives/Aruba WiFi', 'Aruba WiFi'),
        ('Archives/Device Registration', 'Device Registration'),
        ("Archives/DMCA Abuse Complaints", "DMCA's'"),
        ('Archives/General Questions and Complaints', 'General'),
        ('Archives/Hardware', 'Hardware'),
        ('Archives/Internal', 'Internal - General'),
        ('Archives/Internal/Accounts', 'Internal - Accounts'),
        ('Archives/Internal/Dev Team', 'Internal - Dev Team'),
        ('Archives/Internal/Docs', 'Internal - Docs'),
        ('Archives/Internal/Forms', 'Internal - Forms'),
        ('Archives/Internal/Scheduling', 'Internal - Scheduling'),
        ('Archives/Internal/SRS', 'Internal - SRS'),
        ('Archives/Internal/UHTV', 'Internal - UHTV'),
        ('Archives/Internal/Software', 'Software'),
        ('Archives/Internal/Software/VM', 'Software - VM'),
        ('Junk Email', 'Junk'),
        ('Job Applicants', 'Job Applicants'),
    ]

    archive_folders.sort(key=lambda tup: tup[1])

    return archive_folders


def get_plaintext_signature(technician_name):
    return '\n\n\nBest regards,\n' + technician_name + '\nResNet Technician\n\nFor office hours and locations, please visit http://resnet.calpoly.edu.'


class EmailConnectionMixin(object):
    connection_list = None

    def __init__(self, *args, **kwargs):
        super(EmailConnectionMixin, self).__init__(*args, **kwargs)
        if self.server is None:
            self._init_mail_connection()

    def __enter__(self):
        if self.server is None:
            self._init_mail_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        EmailConnectionMixin._release_connection(self.server)

    @staticmethod
    def _new_connection():
        host = settings.INCOMING_EMAIL['IMAP4']['HOST']
        port = settings.INCOMING_EMAIL['IMAP4']['PORT']
        username = settings.INCOMING_EMAIL['IMAP4']['USER']
        password = settings.INCOMING_EMAIL['IMAP4']['PASSWORD']
        ssl = settings.INCOMING_EMAIL['IMAP4']['USE_SSL']
        connection = imapclient.IMAPClient(host, port=port, use_uid=True, ssl=ssl)
        connection.login(username, password)

        return connection

    @classmethod
    def _get_connection(obj):
        if not obj.connection_list:
            obj.connection_list = [(obj._new_connection(), True)]
            return obj.connection_list[0][0]

        for index in range(0, len(obj.connection_list)):
            if obj.connection_list[index][1] is False:
                obj.connection_list[index] = (obj.connection_list[index][0], True)
                return obj.connection_list[index][0]

        return_connection = obj._new_connection()
        obj.connection_list.append((return_connection, True))
        return return_connection

    @classmethod
    def _release_connection(obj, connection):
        for index in range(0, len(obj.connection_list)):
            if obj.connection_list[index][0] is connection:
                obj.connection_list[index] = (connection, False)
                return
        Exception('Could not find connection.')

    @classmethod
    def _reinitialize_connection(cls, connection):
        for index in range(0, len(cls.connection_list)):
            if cls.connection_list[index][0] is connection:
                cls.connection_list[index] = (cls._new_connection(), True)
                return cls.connection_list[index][0]
        Exception('Could not find connection to reinitialize it.')

    def _init_mail_connection(self):
        self.server = EmailConnectionMixin._get_connection()

        try:
            self.server.noop()
        except:
            self.server = EmailConnectionMixin._reinitialize_connection(self.server)


class EmailManager(EmailConnectionMixin):
    server = None

    def decode_header(self, header_bytes):
        """ From https://github.com/maxiimou/imapclient/blob/decode_imap_bytes/imapclient/response_types.py
        Will hopefully be merged into IMAPClient in the future."""

        bytes_output, encoding = header.decode_header(smart_text((header_bytes)))[0]
        if encoding:
            return bytes_output.decode(encoding)
        return bytes_output

    def get_voicemail_attachment(self, uid):
        self.server.select_folder('Voicemails')
        response = self.server.fetch(int(uid), 'BODY[]')

        message = email.message_from_bytes(response[int(uid)][b'BODY[]'])

        for part in message.walk():

            if part.get_content_maintype().startswith('multipart'):
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            file_data = part.get_payload(decode=True)
            self.server.close_folder()

            return (filename, file_data)

        self.server.close_folder()
        raise ValueError('Not a Valid Voicemail Message: No attachment.')

    def move_message(self, mailbox, uid, destination_folder):
        self.server.select_folder(mailbox)

        try:
            self.server.copy(int(uid), destination_folder)
        except:
            print('Copy Failed!')
            return

        self.server.delete_messages(int(uid))
        self.server.expunge()
        self.server.close_folder()

    def delete_voicemail_message(self, uid):
        self.server.select_folder('Voicemails')
        self.move_message('Voicemails', uid, 'Archives/Voicemails')
        self.server.close_folder()

    def get_all_voicemail_messages(self):
        """Get the voicemail messages."""
        voicemails = []

        self.server.select_folder('Voicemails', readonly=True)
        uids = self.server.search()

        # Check for empty inbox
        if not uids:
            return None

        response = self.server.fetch(uids, ['FLAGS', 'BODY[1]'])

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
                "url": "daily_duties/voicemail/" + str(uid),
                "unread": b'\\Seen' not in data[b'FLAGS'],
            }
            print(message)
            voicemails.append(message)

        voicemails.sort(key=itemgetter('date'), reverse=True)

        self.server.close_folder()

        return voicemails

    def get_mailbox_summary(self, mailbox_name):
        self.server.select_folder(mailbox_name)
        message_uids = self.server.search()
        message_uid_fetch_groups = zip_longest(*(iter(message_uids),) * 500)

        messages = []

        for message_uid_group in message_uid_fetch_groups:
            message_uid_group = list(filter(None.__ne__, message_uid_group))
            response = self.server.fetch(message_uid_group, ['ALL'])

            for uid, data in response.items():
                unread = b'\\Seen' not in data[b'FLAGS']
                envelope = data[b'ENVELOPE']
                date = envelope.date
                subject = smart_text(envelope.subject)
                message_from = envelope.from_[0]

                messages.append({
                    'uid': uid,
                    'unread': unread,
                    'date': date,
                    'subject': self.decode_header(subject),
                    'from_name': smart_text(message_from.name) if message_from.name else '',
                    'from_address': smart_text(message_from.mailbox) + '@' + smart_text(message_from.host)
                })

        self.server.close_folder()

        messages.sort(key=itemgetter('date'), reverse=True)
        return messages

    def mark_message_read(self, mailbox_name, uid):
        self.server.select_folder(mailbox_name)
        self.server.add_flags(uid, b'\\Seen')
        self.server.close_folder()

    def mark_message_unread(self, mailbox_name, uid):
        self.server.select_folder(mailbox_name)
        self.server.remove_flags(uid, b'\\Seen')
        self.server.close_folder()

    def mark_message_replied(self, mailbox_name, uid):
        self.server.select_folder(mailbox_name)
        self.server.add_flags(uid, b'\\Answered')
        self.server.close_folder()

    def get_email_message(self, mailbox_name, uid):
        def _convert_list_of_addresses(address_list):
            if not address_list:
                return

            output_list = []

            for address in address_list:
                name = smart_text(address.name) if address.name else ''
                email = smart_text(address.mailbox) + '@' + smart_text(address.host)
                output_list.append((name, email))

            return output_list

        response = cache.get('email:raw:' + mailbox_name + ':' + uid)

        if not response:
            self.server.select_folder(mailbox_name, readonly=True)
            response = self.server.fetch(int(uid), ['ENVELOPE', 'BODY[]'])
            self.server.close_folder()

            cache.set('email:raw:' + mailbox_name + ':' + uid, response, 172800)

        message = email.message_from_bytes(response[int(uid)][b'BODY[]'])
        envelope = response[int(uid)][b'ENVELOPE']

        body_html = ""
        body_plain_text = ""
        attachments = []

        for part in message.walk():
            if part.get_content_type().startswith('multipart'):
                continue
            elif part.get_content_type() is None:
                continue
            elif part.get_content_type() == 'text/html':
                body_html += smart_text(part.get_payload(decode=True), errors='replace')
            elif part.get_content_type() == 'text/plain':
                body_plain_text += smart_text(part.get_payload(decode=True), errors='replace')
            else:
                attachment = {
                    'filename': part.get_filename(),
                    'filedata': part.get_payload(decode=True),
                    'filetype': part.get_content_type(),
                    'content_id': part.get('Content-ID'),
                }
                attachments.append(attachment)

        message = {
            'to': _convert_list_of_addresses(envelope.to),
            'from': _convert_list_of_addresses(envelope.from_),
            'cc': _convert_list_of_addresses(envelope.cc),
            'reply_to': _convert_list_of_addresses(envelope.reply_to) if envelope.reply_to else _convert_list_of_addresses(envelope.from_),
            'date': envelope.date,
            'message-id': smart_text(envelope.message_id),
            'subject': self.decode_header(envelope.subject),
            'body_html': body_html,
            'body_plain_text': body_plain_text,
            'attachments': attachments,
            'is_html': len(body_html) > len(body_plain_text),
            'path': mailbox_name + '/' + uid,
            'mailbox': mailbox_name,
            'uid': uid,
        }

        return message

    def send_message(self, message_dict):
        with mail.get_connection() as connection:
            email = EmailMessage()
            email.connection = connection

            email.to = message_dict['to']
            email.cc = message_dict['cc']
            email.from_email = message_dict['from']
            email.reply_to = [message_dict['from']]
            email.subject = message_dict['subject']
            email.body = message_dict['body']

            if message_dict['is_html']:
                email.content_subtype = 'html'

            email.send()
            self.server.append('Sent Items', email.message().as_bytes())

            if message_dict.get('in_reply_to'):
                reply_information = message_dict['in_reply_to'].rsplit('/', 1)
                self.mark_message_replied(reply_information[0], reply_information[1])


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

    def get_voicemail(self):
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
            data = DailyDuties.objects.get(name='voicemail')

            count = self.server.select_folder('Voicemails', readonly=True)[b'EXISTS']
            self.server.close_folder()

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
            self.server.close_folder()

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
            logger.exception(message)
            tickets["count"] = 0
            tickets["status_color"] = RED
            tickets["last_checked"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            tickets["last_user"] = "Connection Error!"

        return tickets
