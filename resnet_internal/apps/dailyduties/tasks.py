"""
.. module:: resnet_internal.apps.dailyduties.tasks
   :synopsis: University Housing Internal Daily Duty Tasks.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>
"""

import json
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.cache import cache
from django.core.urlresolvers import reverse
from html2text import html2text
import requests


try:
    from uwsgidecorators import timer
except ImportError:
    def timer(time, **kwargs):
        def wrap(f):
            def wrap_2(num):
                return f(num)
            return wrap_2
        return wrap

from .utils import EmailManager, EmailConnectionMixin


@timer(60)
def update_slack_voicemail(num):
    previous_voicemail_messages = cache.get('previous_voicemail_messages')

    with EmailManager() as email_manager:
        current_voicemails = email_manager.get_all_voicemail_messages()

    for voicemail in current_voicemails:
        del voicemail['unread']

    if previous_voicemail_messages is not None:
        new_voicemails = [voicemail for voicemail in current_voicemails if voicemail not in previous_voicemail_messages]

        for voicemail in new_voicemails:
            text = '<%s|New Voicemail> from %s at %s!' % (urljoin(settings.DEFAULT_BASE_URL, reverse('dailyduties:voicemail_list')),
                                                          voicemail['sender'],
                                                          str(voicemail['date']))

            icon_url = urljoin(settings.DEFAULT_BASE_URL, static('images/icons/voicemail.png'))

            payload = {'text': text, 'icon_url': icon_url, 'channel': settings.SLACK_VM_CHANNEL}
            url = settings.SLACK_WEBHOOK_URL
            headers = {'content-type': 'application/json'}
            requests.post(url, data=json.dumps(payload), headers=headers)

    cache.set('previous_voicemail_messages', current_voicemails, 10 * 60)


@timer(60)
def update_slack_email(num):
    previous_email_messages = cache.get('previous_email_messages')

    with EmailManager() as email_manager:
        current_emails, num_available_messages = email_manager.get_messages('INBOX', '')  # noqa
        cache.set('previous_email_messages', current_emails, 10 * 60)

        if previous_email_messages is not None:
            new_emails = []

            for current_email in current_emails:
                found = False

                for prev_email in previous_email_messages:
                    if current_email['uid'] == prev_email['uid']:
                        found = True
                        break

                if not found:
                    new_emails.append(current_email)

            if new_emails:
                slack_attachments = []

                for email in new_emails:
                    email_message = email_manager.get_email_message('INBOX', email['uid'])

                    attachment = {
                        'fallback': 'New email message from %s' % email['sender_name'],
                        'color': 'good',
                        'author_name': email['sender_name'] + ' (' + email['sender_address'] + ')',
                        'title': 'Subject: ' + email['subject'],
                        'title_link': urljoin(settings.DEFAULT_BASE_URL, reverse('dailyduties:email_view_message', kwargs={'mailbox_name': 'INBOX', 'uid': email['uid']})),
                        'text': email_message['body_plain_text'] if email_message['body_plain_text'] else html2text(email_message['body_html']),

                    }
                    slack_attachments.append(attachment)

                payload = {'text': 'New Email Messages!' if len(new_emails) > 1 else 'New Email Message!',
                           'icon_url': urljoin(settings.DEFAULT_BASE_URL, static('images/icons/email.png')),
                           'channel': settings.SLACK_EMAIL_CHANNEL,
                           'attachments': slack_attachments}

                url = settings.SLACK_WEBHOOK_URL
                headers = {'content-type': 'application/json'}

                requests.post(url, data=json.dumps(payload), headers=headers)


@timer(60, target='workers')
def keep_imap_alive(num):
    EmailConnectionMixin.send_noop_to_all_connections()
