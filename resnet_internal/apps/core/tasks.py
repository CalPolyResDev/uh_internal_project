"""
.. module:: resnet_internal.apps.core.tasks
   :synopsis: ResNet Internal Core Tasks.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>
"""

from urllib.parse import urljoin
import json

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.cache import cache
from django.core.urlresolvers import reverse
from uwsgidecorators import timer
import requests

from .utils import NetworkReachabilityTester


@timer(60)
def update_slack_network_status(num):
    previous_down_devices = cache.get('core_slack_previous_down_devices')

    if previous_down_devices is None:
        previous_down_devices = []

    device_statuses = NetworkReachabilityTester.get_network_device_reachability(10)

    down_devices = [device for device in device_statuses if not device['status']]
    new_down_devices = [down_device for down_device in down_devices if down_device not in previous_down_devices]

    cache.set('core_slack_previous_down_devices', down_devices, 10 * 60)

    if new_down_devices:
        slack_attachments = []

        if len(new_down_devices) < len(device_statuses) / 4:  # Less than 25% of network
            for device in new_down_devices:
                attachment = {
                    'fallback': 'Network Device Down: ' + device['display_name'],
                    'color': 'danger',
                    'title': device['display_name'],
                    'title_link': urljoin(settings.DEFAULT_BASE_URL, reverse('home')),
                    'fields': [
                        {'title': 'IP Address', 'value': device['ip_address']},
                        {'title': 'DNS Name', 'value': device['dns_name']},
                    ]
                }
                slack_attachments.append(attachment)
        else:  # Major issues
            attachment = {
                'fallback': '%d Network Devices Down!' % len(new_down_devices),
                'color': 'danger',
                'title': 'Many Network Devices Down!',
                'title_link': urljoin(settings.DEFAULT_BASE_URL, reverse('home')),
                'fields': [
                    {'title': 'Device Count', 'value': len(new_down_devices)},
                    {'title': 'Note', 'value': 'Because so many devices went down in the last minute, this is either a server error or a major network outage.'},
                ]
            }
            slack_attachments.append(attachment)

        payload = {'text': 'Network Devices are Down!' if len(new_down_devices) > 1 else 'A Network Device is Down!',
                           'icon_url': urljoin(settings.DEFAULT_BASE_URL, static('images/icons/aruba.png')),
                           'channel': settings.SLACK_NETWORK_STATUS_CHANNEL,
                           'attachments': slack_attachments}

        url = settings.SLACK_WEBHOOK_URL
        headers = {'content-type': 'application/json'}
        requests.post(url, data=json.dumps(payload), headers=headers)