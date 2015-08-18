"""
.. module:: resnet_internal.apps.core.utils
   :synopsis: ResNet Internal Core Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging
import os
from copy import deepcopy
from itertools import chain

from srsconnector.models import ServiceRequest

from .models import NetworkDevice

logger = logging.getLogger(__name__)


class NetworkReachabilityTester:

    @staticmethod
    def _is_device_reachable(ip_address):
        response = os.system("ping -c 1 -t 1 " + ip_address)
        return True if response == 0 else False
    
    @staticmethod
    def get_network_device_reachability():
        reachability_responses = []
        
        network_devices = NetworkDevice.objects.all()
        
        for network_device in network_devices:
            reachability_responses.append({'display_name': network_device.display_name,
                                           'dns_name': network_device.dns_name,
                                           'ip_address': network_device.ip_address,
                                           'status': NetworkReachabilityTester._is_device_reachable(network_device.ip_address),
                                           })
        return reachability_responses


def dict_merge(base, merge):
    """ Recursively merges dictionaries.

    :param base: The base dictionary.
    :type base: dict
    :param merge: The dictionary to merge with base.
    :type merge: dict

    """

    if not isinstance(merge, dict):
        return merge
    result = deepcopy(base)

    for key, value in merge.items():
        if key in result and isinstance(result[key], dict):
                result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def get_ticket_list(user):
    print('Here')
    unassigned_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET").exclude(status=4).exclude(status=8)
    assigned_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET", assigned_person=str(user.get_full_name())).exclude(status=4).exclude(status=8)

    ticket_list = list(chain(unassigned_tickets, assigned_tickets))
    ticket_list.sort(key=lambda ticket: ticket.date_created, reverse=True)
    
    return ticket_list
