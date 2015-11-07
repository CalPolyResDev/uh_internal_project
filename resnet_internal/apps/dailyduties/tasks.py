"""
.. module:: resnet_internal.apps.dailyduties.tasks
   :synopsis: ResNet Internal Daily Duty Tasks.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com
"""

import json

from django.conf import settings
from django.core.cache import cache
from uwsgidecorators import timer
import requests

from .utils import EmailManager


@timer(60)
def update_slack(num):
    previous_voicemail_messages = cache.get('previous_voicemail_messages')

    with EmailManager() as email_manager:
        current_voicemails = email_manager.get_all_voicemail_messages()

    if previous_voicemail_messages is None:
        previous_voicemail_messages = current_voicemails
    else:
        new_voicemails = [voicemail for voicemail in current_voicemails if voicemail not in previous_voicemail_messages]

        for voicemail in new_voicemails:
            text = '<https://internal.resnet.calpoly.edu/daily_duties/voicemail/list/|New Voicemail> from %s at %s!' % (voicemail['sender'], str(voicemail['date']))
            icon_url = 'https://internal.resnet.calpoly.edu/static/images/icons/voicemail.png'

            payload = {'text': text, 'icon_url': icon_url}
            url = settings.SLACK_VM_URL
            headers = {'content-type': 'application/json'}

            requests.post(url, data=json.dumps(payload), headers=headers)

    cache.set('previous_voicemail_messages', 10 * 60)
