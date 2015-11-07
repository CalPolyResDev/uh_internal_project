"""
.. module:: resnet_internal.apps.dailyduties.tasks
   :synopsis: ResNet Internal Daily Duty Tasks.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com
"""

from urllib.parse import urljoin
import json

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.cache import cache
from django.core.urlresolvers import reverse
from uwsgidecorators import timer
import requests

from .utils import EmailManager


@timer(60)
def update_slack_voicemail(num):
    previous_voicemail_messages = cache.get('previous_voicemail_messages')

    with EmailManager() as email_manager:
        current_voicemails = email_manager.get_all_voicemail_messages()

    if previous_voicemail_messages is not None:
        new_voicemails = [voicemail for voicemail in current_voicemails if voicemail not in previous_voicemail_messages]

        for voicemail in new_voicemails:
            text = '<%s|New Voicemail> from %s at %s!' % (urljoin(settings.DEFAULT_BASE_URL, reverse('voicemail_list')),
                                                          voicemail['sender'],
                                                          str(voicemail['date']))

            icon_url = urljoin(settings.DEFAULT_BASE_URL, static('images/icons/voicemail.png'))

            payload = {'text': text, 'icon_url': icon_url, 'channel': settings.SLACK_VM_CHANNEL}
            url = settings.SLACK_WEBHOOK_URL
            headers = {'content-type': 'application/json'}
            requests.post(url, data=json.dumps(payload), headers=headers)

    cache.set('previous_voicemail_messages', current_voicemails, 10 * 60)
