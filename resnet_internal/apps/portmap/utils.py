"""
.. module:: resnet_internal.apps.network.utils
   :synopsis: University Housing Internal Network Utilities.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from sys import platform
import logging
import os

from django.core.cache import cache

from .models import NetworkInfrastructureDevice, NetworkDevice

logger = logging.getLogger(__name__)


def port_is_down(port):
    return cache.get(down_device_cache_key(port.upstream_device)) and not cache.get(up_device_cache_key(port.upstream_device))


def get_dns_name(device):
    if isinstance(device, NetworkDevice):
        return device.dns_name
    else:
        return device['dns_name']


def down_device_cache_key(device):
    return 'down_device::' + get_dns_name(device)


def up_device_cache_key(device):
    return 'up_device::' + get_dns_name(device)


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
