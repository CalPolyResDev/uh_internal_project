"""
.. module:: resnet_internal.apps.portmap.management.commands.update_airwaves_ids
   :synopsis: University Housing Internal Network Airwaves ID Update

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand

from ...airwaves.search import DeviceQuery
from ...models import NetworkDevice


class Command(BaseCommand):

    def handle(self, *args, **options):
        def update_network_device(network_device):
            if network_device.mac_address:
                queryResult = DeviceQuery(network_device.mac_address)

                if len(queryResult.results) == 1:
                    network_device.airwaves_id = queryResult.results[0]
                    network_device.save()
            elif network_device.ip_address:
                queryResult = DeviceQuery(network_device.ip_address)

                if len(queryResult.results) == 1:
                    network_device.airwaves_id = queryResult.results[0]
                    network_device.save()

        with ThreadPoolExecutor(max_workers=25) as pool:
            pool.map(update_network_device, NetworkDevice.objects.all())
