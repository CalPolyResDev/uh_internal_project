"""
.. module:: resnet_internal.apps.core.utils
   :synopsis: ResNet Internal Core Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from copy import deepcopy
from operator import itemgetter
from sys import platform
import logging
import os

from django.core.cache import cache
from srsconnector.models import ServiceRequest

from ...settings.base import technician_access_test
from .models import NetworkDevice


logger = logging.getLogger(__name__)


class NetworkReachabilityTester:

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

        network_devices = NetworkDevice.objects.all()

        for network_device in network_devices:
            reachability_responses.append({'display_name': network_device.display_name,
                                           'dns_name': network_device.dns_name,
                                           'ip_address': network_device.ip_address,
                                           'status': NetworkReachabilityTester._is_device_reachable(network_device.ip_address, timeout),
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
    user_teams = []
    if user.is_rn_staff:
        user_teams.append('SA University Housing')
    if technician_access_test(user):
        user_teams.append('SA RESNET')

    cache_key = 'ticket_list:' + str(user_teams)

    tickets = cache.get(cache_key)

    if tickets is None:
        ticket_queryset = ServiceRequest.objects.filter(assigned_team__in=user_teams).exclude(status=4).exclude(status=8)

        tickets = list({'ticket_id': ticket.ticket_id,
                        'requestor_full_name': ticket.requestor_full_name,
                        'status': ticket.status,
                        'summary': ticket.summary,
                        'date_created': ticket.date_created,
                        'date_updated': ticket.date_updated,
                        'assigned_person': ticket.assigned_person,
                        'updater_is_technician': ticket.updater_is_technician,
                        'date_updated': ticket.date_updated,
                        } for ticket in ticket_queryset)

        tickets = sorted(tickets, key=itemgetter('date_created'), reverse=True)
        cache.set(cache_key, tickets, 60 * 5)

    return tickets
