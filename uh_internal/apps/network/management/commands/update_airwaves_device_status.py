"""
.. module:: uh_internal.apps.portmap.management.commands.update_airwaves_device_status
   :synopsis: University Housing Internal Network Airwaves Device Status Update

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand

from ...airwaves.data import DeviceInfo
from ...models import NetworkDevice


class Command(BaseCommand):

    def handle(self, *args, **options):
        def update_network_device(network_device):
            if network_device.airwaves_id:
                device_info = DeviceInfo(network_device.airwaves_id)
                network_device.airwaves_is_up = device_info.up
                network_device.save()

        with ThreadPoolExecutor(max_workers=25) as pool:
            pool.map(update_network_device, NetworkDevice.objects.all())
