"""
.. module:: resnet_internal.apps.dailyduties.utils
   :synopsis: University Housing Internal Daily Duty Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from email import header
from imaplib import IMAP4
from itertools import zip_longest
from operator import itemgetter
from ssl import SSLError, SSLEOFError, CERT_NONE
from threading import Lock
import email
import itertools
import logging
import os
import socket

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.core.mail.message import EmailMessage
from django.db import DatabaseError
from django.utils.encoding import smart_text
from html2text import html2text
from srsconnector.models import ServiceRequest
import imapclient

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
        ('Archives/Internal/SRS General', 'Internal - SRS'),
        ('Archives/Internal/UHTV', 'Internal - UHTV'),
        ('Archives/Software', 'Software'),
        ('Archives/Software/VM', 'Software - VM'),
        ('Junk Email', 'Junk'),
        ('Job Applicants', 'Job Applicants'),
    ]

    archive_folders.sort(key=lambda tup: tup[1])

    return archive_folders


def get_plaintext_signature(technician_name):
    return '\n\n\nBest regards,\n' + technician_name + '\nResNet Technician\n\nFor office hours and locations, please visit http://resnet.calpoly.edu.'


class EmailConnectionMixin(object):
    connection_list = None
    lock = Lock()

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

        connection = None
        attempt_number = 0
        while not connection and attempt_number < 10:
            try:
                # TODO: Remove ssl_context when certificate comes in.
                ssl_context = imapclient.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = CERT_NONE

                connection = imapclient.IMAPClient(host, port=port, use_uid=True, ssl=ssl, ssl_context=ssl_context)
                connection.login(username, password)
            except (OSError, IMAP4.error) as exc:
                logger.error("Can't connect to IMAP server: %s, trying again." % str(exc), exc_info=True)
                connection = None
            attempt_number += 1

        return connection

    @classmethod
    def _get_connection(cls):
        with cls.lock:
            if not cls.connection_list:
                cls.connection_list = [(cls._new_connection(), True)]
                return cls.connection_list[0][0]

            for index in range(0, len(cls.connection_list)):
                if cls.connection_list[index][1] is False:
                    cls.connection_list[index] = (cls.connection_list[index][0], True)
                    return cls.connection_list[index][0]

            return_connection = cls._new_connection()
            cls.connection_list.append((return_connection, True))
            return return_connection

    @classmethod
    def _release_connection(cls, connection):
        with cls.lock:
            for index in range(0, len(cls.connection_list)):
                if cls.connection_list[index][0] is connection:
                    cls.connection_list[index] = (connection, False)
                    return
            Exception('Could not find connection.')

    @classmethod
    def _reinitialize_connection(cls, connection):
        with cls.lock:
            for index in range(0, len(cls.connection_list)):
                if cls.connection_list[index][0] is connection:
                    cls.connection_list[index] = (cls._new_connection(), True)
                    return cls.connection_list[index][0]
            Exception('Could not find connection to reinitialize it.')

    @classmethod
    def _get_tested_connection(cls):
        connection = cls._get_connection()

        try:
            connection.noop()
        except:
            connection = cls._reinitialize_connection(connection)

        return connection

    @classmethod
    def send_noop_to_all_connections(cls):
        with cls.lock:
            if cls.connection_list:
                for index in range(0, len(cls.connection_list)):
                    if cls.connection_list[index][1] is False:
                        try:
                            cls.connection_list[index][0].noop()
                        except:
                            cls.connection_list[index] = (cls._new_connection(), False)

    def _init_mail_connection(self):
        self.server = EmailConnectionMixin._get_tested_connection()


class EmailManager(EmailConnectionMixin):
    server = None

    SEARCH_MAILBOXES = [
        'Archives/Aruba Ethernet',
        'Archives/Aruba WiFi',
        'Archives/Device Registration',
        "Archives/DMCA Abuse Complaints",
        'Archives/General Questions and Complaints',
        'Archives/Hardware',
        'Archives/Internal',
        'Archives/Internal/Accounts',
        'Archives/Internal/Dev Team',
        'Archives/Internal/Docs',
        'Archives/Internal/Forms',
        'Archives/Internal/Scheduling',
        'Archives/Internal/SRS General',
        'Archives/Internal/UHTV',
        'Archives/Software',
        'Archives/Software/VM',
        'Junk Email',
        'Job Applicants',
        'INBOX',
        'Sent Items',
    ]

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
            return

        self.server.delete_messages(int(uid))
        self.server.expunge()
        self.server.close_folder()

    def delete_voicemail_message(self, uid):
        self.move_message('Voicemails', uid, 'Archives/Voicemails')

    def get_all_voicemail_messages(self):
        """Get the voicemail messages."""
        voicemails = []

        self.server.select_folder('Voicemails', readonly=True)
        uids = self.server.search()

        # Check for empty inbox
        if not uids:
            return []

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
            voicemails.append(message)

        voicemails.sort(key=itemgetter('date'), reverse=True)

        self.server.close_folder()

        return voicemails

    def _create_uid_fetch_groups(self, uids):
        return zip_longest(*(iter(uids),) * 500)

    def _get_uids_and_dates_for_mailbox(self, mailbox_name, search_string, **kwargs):
        server = kwargs.get('connection', self.server)

        server.select_folder(mailbox_name)
        imap_search_string = 'TEXT "' + search_string + '"' if search_string else 'ALL'

        unsorted_message_uids = server.search(imap_search_string)
        message_uid_fetch_groups = self._create_uid_fetch_groups(unsorted_message_uids)
        unsorted_messages = []

        for message_uid_group in message_uid_fetch_groups:
            message_uid_group = list(filter(None.__ne__, message_uid_group))
            response = server.fetch(message_uid_group, ['INTERNALDATE'])

            for uid, data in response.items():
                # A deleted message that is not yet expunged will not have the INTERNALDATE
                # key set but will be in this list. These should be ommitted.
                date = data.get(b'INTERNALDATE', None)
                if date is not None:
                    unsorted_messages.append((uid, date))

        server.close_folder()
        return sorted(unsorted_messages, key=itemgetter(1), reverse=True)

    def _get_message_summaries(self, mailbox_name, message_uids, **kwargs):
        server = kwargs.get('connection', self.server)

        server.select_folder(mailbox_name)

        message_uid_fetch_groups = self._create_uid_fetch_groups(message_uids)

        messages = []

        for message_uid_group in message_uid_fetch_groups:
            message_uid_group = list(filter(None.__ne__, message_uid_group))
            response = server.fetch(message_uid_group, ['FLAGS', 'INTERNALDATE', 'RFC822.SIZE', 'ENVELOPE'])

            for uid, data in response.items():
                unread = b'\\Seen' not in data[b'FLAGS']
                replied = b'\\Answered' in data[b'FLAGS']
                envelope = data[b'ENVELOPE']
                date = envelope.date
                subject = smart_text(envelope.subject)

                message_from = envelope.from_[0] if envelope.from_ else None
                message_to = envelope.to[0] if envelope.to else None
                sender_address = message_to if mailbox_name == 'Sent Items' else message_from

                messages.append({
                    'mailbox': mailbox_name,
                    'uid': uid,
                    'unread': unread,
                    'replied': replied,
                    'date': date,
                    'subject': self.decode_header(subject),
                    'sender_name': self.decode_header(sender_address.name) if sender_address else '',
                    'sender_address': smart_text(sender_address.mailbox) + '@' + smart_text(sender_address.host) if sender_address else None,
                })

        server.close_folder()
        return messages

    def get_messages(self, mailbox_name, search_string, **kwargs):
        message_range = kwargs.get('range')

        if mailbox_name:
            message_uids = [message[0] for message in sorted(self._get_uids_and_dates_for_mailbox(mailbox_name, search_string), key=itemgetter(1), reverse=True)]

            num_available_messages = len(message_uids)

            if message_range:
                if message_range[0] > len(message_uids) - 1:
                    message_range[0] = 0
                if message_range[1] > len(message_uids) - 1:
                    message_range[1] = len(message_uids) - 1

                message_uids = message_uids[message_range[0]:message_range[1] + 1]

            messages = self._get_message_summaries(mailbox_name, message_uids)
            messages.sort(key=itemgetter('date'), reverse=True)
            return (messages, num_available_messages)
        else:
            def retrieve_results_for_mailbox(mailbox_name):
                message_results = []
                connection = EmailConnectionMixin._get_tested_connection()

                uids_and_dates = self._get_uids_and_dates_for_mailbox(mailbox_name, search_string, connection=connection)
                for uid, date in uids_and_dates:
                    message_results.append({
                        'uid': uid,
                        'date': date,
                        'mailbox_name': mailbox_name,
                    })

                EmailConnectionMixin._release_connection(connection)
                return message_results

            with ThreadPoolExecutor(max_workers=20) as pool:
                message_results = pool.map(retrieve_results_for_mailbox, self.SEARCH_MAILBOXES)
            message_results = list(itertools.chain(*message_results))  # Flatten list of lists

            # Sort and select range
            message_results.sort(key=itemgetter('date'), reverse=True)
            total_available_messages = len(message_results)

            if message_range:
                if message_range[0] > len(message_results) - 1:
                    message_range[0] = 0
                if message_range[1] > len(message_results) - 1:
                    message_range[1] = len(message_results) - 1

                message_results = message_results[message_range[0]:message_range[1] + 1]

            message_results_by_mailbox = defaultdict(list)

            # Retrieve messages from mailboxes
            messages = []

            def retrieve_messages_for_mailbox(mailbox_name, partial_messages):
                connection = EmailConnectionMixin._get_tested_connection()
                messages.extend(self._get_message_summaries(mailbox_name, [message['uid'] for message in partial_messages], connection=connection))
                EmailConnectionMixin._release_connection(connection)

            for message in message_results:
                message_results_by_mailbox[message['mailbox_name']].append(message)

            with ThreadPoolExecutor(max_workers=20) as pool:
                pool.map(lambda mailbox_results: retrieve_messages_for_mailbox(mailbox_results[0], mailbox_results[1]), message_results_by_mailbox.items())

            # Sort and return
            messages.sort(key=itemgetter('date'), reverse=True)
            return (messages, total_available_messages)

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

        cache_key = 'email:raw:' + mailbox_name + ':' + str(uid)
        response = cache.get(cache_key)

        if not response:
            self.server.select_folder(mailbox_name, readonly=True)
            response = self.server.fetch(int(uid), ['ENVELOPE', 'BODY[]'])
            self.server.close_folder()

            cache.set(cache_key, response, 172800)

        try:
            message = email.message_from_bytes(response[int(uid)][b'BODY[]'])
            envelope = response[int(uid)][b'ENVELOPE']
        except KeyError:
            return None

        body_html = ""
        body_plain_text = ""
        attachments = []

        for part in message.walk():
            if part.get_content_type().startswith('multipart') or part.get_content_type().startswith('message'):
                continue
            elif part.get_content_type() is None:
                continue
            elif part.get_content_type() == 'text/html':
                body_html += smart_text(part.get_payload(decode=True), errors='replace')
            elif part.get_content_type() == 'text/plain':
                body_plain_text += '\n' + smart_text(part.get_payload(decode=True), errors='replace')
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
            'path': mailbox_name + '/' + str(uid),
            'mailbox': mailbox_name,
            'uid': uid,
            'in_reply_to': envelope.in_reply_to,
            'references': message.get('References')
        }

        return message

    def send_message(self, message_dict):
        with mail.get_connection() as connection:
            email_message = EmailMessage()
            email_message.connection = connection

            email_message.to = message_dict['to']
            email_message.cc = message_dict['cc']
            email_message.from_email = message_dict['from']
            email_message.reply_to = [message_dict['from']]
            email_message.subject = message_dict['subject']
            email_message.body = message_dict['body']
            email_message.extra_headers['message-id'] = '<' + datetime.strftime(datetime.utcnow(), '%d-%m-%Y-%H-%m-%S-%f') + '.' + str(os.getpid()) + '@' + socket.gethostname() + '>'

            for attachment in message_dict['attachments']:
                email_message.attach(attachment.name, attachment.read(), attachment.content_type)

            if message_dict.get('in_reply_to'):
                reply_information = message_dict['in_reply_to'].rsplit('/', 1)
                self.mark_message_replied(reply_information[0], reply_information[1])

                original_message = self.get_email_message(reply_information[0], reply_information[1])
                email_message.extra_headers['In-Reply-To'] = original_message['message-id'].replace(',', ' ').replace('\n', '').replace('\r', '')

                if original_message.get('references'):
                    email_message.extra_headers['References'] = (original_message['references'].strip() + ' ' + original_message['message-id']).replace(',', ' ').replace('\n', '').replace('\r', '')
                else:
                    email_message.extra_headers['References'] = original_message['message-id'].strip()

            if message_dict['is_html']:
                email_message.content_subtype = 'html'

            email_message.send()
            self.server.append('Sent Items', email_message.message().as_bytes(), flags=[b'\\Seen'])

    def create_ticket_from_email(self, mailbox_name, uid, requestor_username, full_name):
        message_dict = self.get_email_message(mailbox_name, uid)

        plain_text_body = message_dict['body_plain_text'] if not message_dict['is_html'] else html2text(message_dict['body_html'])
        service_request = ServiceRequest(
            status='Work In Progress',
            priority='Low',
            assigned_team='SA RESNET',
            requestor_username=requestor_username,
            contact_method='Email',
            general_issue='Network Services',
            specific_issue='Network Service Problem',
            residence_hall_related=True,
            summary=message_dict['subject'],
            description=plain_text_body,
            work_log='Created ticket for %s.' % full_name,
        )
        service_request.save()

        if service_request.requestor_housing_address:
            requestor_address = service_request.requestor_housing_address
            requestor_address = requestor_address.replace('Poly Canyon Village', 'PCV').replace('Cerro Vista', 'CV')
        elif service_request.requestor_building and service_request.requestor_room:
            requestor_address = service_request.requestor_building + ' ' + service_request.requestor_room
        else:
            requestor_address = None

        if requestor_address:
            service_request.summary = requestor_address + ': ' + service_request.summary

        return service_request.ticket_id


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
