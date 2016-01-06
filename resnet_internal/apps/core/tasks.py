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

PREVIOUS_DOWN_DEVICE_TIMEOUT = 60 * 60  # s
MAJOR_OUTAGE_CACHE_KEY = 'down_device::large_outage'
MAJOR_OUTAGE_THRESHOLD = .25
REACHABILITY_TESTER_PING_TIMEOUT = 10  # ms


@timer(60)
def update_slack_network_status(num):
    device_statuses = NetworkReachabilityTester.get_network_device_reachability(REACHABILITY_TESTER_PING_TIMEOUT)
    down_devices = [device for device in device_statuses if not device['status']]

    if down_devices:
        slack_attachments = []

        if len(down_devices) < len(device_statuses) * MAJOR_OUTAGE_THRESHOLD:  # Less than threshold
            for device in down_devices:
                device_cache_key = 'down_device::' + device['ip_address']

                if cache.get(device_cache_key) is None:
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

                cache.set(device_cache_key, device, PREVIOUS_DOWN_DEVICE_TIMEOUT)
        else:  # Major issues

            if cache.get(MAJOR_OUTAGE_CACHE_KEY) is None:
                attachment = {
                    'fallback': '%d Network Devices Down!' % len(down_devices),
                    'color': 'danger',
                    'title': 'Many Network Devices Down!',
                    'title_link': urljoin(settings.DEFAULT_BASE_URL, reverse('home')),
                    'fields': [
                        {'title': 'Device Count', 'value': len(down_devices)},
                        {'title': 'Note', 'value': 'Because so many devices are down, this is either a server error or a major network outage.'},
                    ]
                }
                slack_attachments.append(attachment)
                cache.set(MAJOR_OUTAGE_CACHE_KEY, True, PREVIOUS_DOWN_DEVICE_TIMEOUT)

        payload = {'text': 'Network Devices are Down!' if len(slack_attachments) > 1 else 'A Network Device is Down!',
                           'icon_url': urljoin(settings.DEFAULT_BASE_URL, static('images/icons/aruba.png')),
                           'channel': settings.SLACK_NETWORK_STATUS_CHANNEL,
                           'attachments': slack_attachments}

        url = settings.SLACK_WEBHOOK_URL
        headers = {'content-type': 'application/json'}
        requests.post(url, data=json.dumps(payload), headers=headers)
