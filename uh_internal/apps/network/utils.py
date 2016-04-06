"""
.. module:: resnet_internal.apps.network.utils
   :synopsis: University Housing Internal Network Utilities.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from sys import platform
import logging
import os
import re

from django.core.cache import cache

from .models import NetworkInfrastructureDevice, NetworkDevice


logger = logging.getLogger(__name__)


def device_is_down(device):
    return cache.get(down_device_cache_key(device)) and not cache.get(up_device_cache_key(device))


def get_dns_name(device):
    if isinstance(device, NetworkDevice):
        return device.dns_name
    else:
        return device['dns_name']


def down_device_cache_key(device):
    return 'down_device::' + get_dns_name(device)


def up_device_cache_key(device):
    return 'up_device::' + get_dns_name(device)


def validate_mac(mac_address):
    PATTERN = r'^[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\1[0-9a-f]{2}){4}$'

    return bool(re.match(PATTERN, mac_address.lower()))


def mac_address_with_colons(mac_address):
    if not validate_mac(mac_address):
        raise ValueError('Invalid MAC Address: ' + mac_address)

    mac_address = mac_address.upper()

    if ':' in mac_address:
        return mac_address
    elif '-' in mac_address:
        return mac_address.replace('-', ':')
    else:
        return ':'.join(re.findall('..', mac_address))


def mac_address_no_separator(mac_address):
    if not validate_mac(mac_address):
        raise ValueError('Invalid MAC Address: ' + mac_address)

    return mac_address.replace('-', '').replace(':', '')


class NetworkReachabilityTester(object):

    @staticmethod
    def _is_device_reachable(ip_address, timeout):
        if platform == 'darwin':
            response = os.system("ping -c 1 -t " + str(timeout) + " " + ip_address + ' > /dev/null 2>&1')
        else:
            response = os.system("ping -c 1 -w " + str(timeout) + " " + ip_address + ' > /dev/null 2>&1')

        return True if response == 0 else False

    @staticmethod
    def get_network_device_reachability(timeout):
        reachability_responses = []

        network_devices = NetworkInfrastructureDevice.objects.all()

        for network_device in network_devices:
            reachability_responses.append({'display_name': network_device.display_name,
                                           'dns_name': network_device.dns_name,
                                           'ip_address': network_device.ip_address,
                                           'status': NetworkReachabilityTester._is_device_reachable(network_device.ip_address, timeout),
                                           })
        return reachability_responses
