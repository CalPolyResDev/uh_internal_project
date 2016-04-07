"""
.. module:: uh_internal.apps.network.clearpass.utils
   :synopsis: University Housing Internal Clearpass Utilities

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from concurrent.futures import ThreadPoolExecutor

from ..airwaves.data import ClientInfo
from ..airwaves.exceptions import ClientLookupError
from ..clearpass.configuration import Endpoint
from ..clearpass.exceptions import EndpointLookupError
from ..models import ClearPassLoginAttempt


def get_user_login_attempts(email_address):
    return ClearPassLoginAttempt.objects.filter(username=email_address)


def get_user_device_list(email_address):
    return list(get_user_login_attempts(email_address).order_by('client_mac_address').distinct('client_mac_address').values_list('client_mac_address', flat=True))


def get_device_login_attempts(mac_address):
    return ClearPassLoginAttempt.objects.filter(client_mac_address=mac_address)


def get_user_devices_info(email_address):
    user_devices = get_user_device_list(email_address)

    def get_client_info(user_device):
        try:
            return ClientInfo(user_device)
        except ClientLookupError:
            return None

    def get_endpoint(user_device):
        try:
            return Endpoint(user_device)
        except EndpointLookupError:
            return None

    airwaves_device_futures = {}
    airwaves_devices_info = {}

    clearpass_devices_futures = {}
    clearpass_devices_info = {}

    with ThreadPoolExecutor(max_workers=50) as pool:
        for user_device in user_devices:
            airwaves_device_futures[user_device] = pool.submit(lambda: get_client_info(user_device))
            clearpass_devices_futures[user_device] = pool.submit(lambda: get_endpoint(user_device))

        for user_device, user_device_future in airwaves_device_futures.items():
            airwaves_devices_info[user_device] = user_device_future.result()

        for user_device, user_device_future in clearpass_devices_futures.items():
            clearpass_devices_info[user_device] = user_device_future.result()

    user_devices_info = {}

    for user_device in user_devices:
        user_devices_info[user_device] = {
            'clearpass': clearpass_devices_info[user_device],
            'airwaves': airwaves_devices_info[user_device],
            'login_attempts': ClearPassLoginAttempt.objects.filter(client_mac_address=user_device).order_by('-time'),
        }

    return user_devices_info
