"""
.. module:: resnet_internal.apps.portmap.airwaves.search
   :synopsis: Airwaves Search

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from urllib.parse import urlencode

from .connector import AirwavesAPIConnector


class DeviceQuery(AirwavesAPIConnector):

    def __init__(self, search_string):
        super().__init__()

        response = self.get_XML('ap_search.xml?' + urlencode({'query': search_string}))

        self.results = []

        if 'record' in response['amp:amp_ap_search']:
            for record in self._ensure_list(response['amp:amp_ap_search']['record']):
                self.results.append(int(record['@id']))


class ClientQuery(AirwavesAPIConnector):

    def __init__(self, search_string):
        super().__init__()

        response = self.get_XML('client_search.xml?' + urlencode({'query': search_string}))

        self.results = []

        if 'record' in response['amp:amp_client_search']:
            for record in self._ensure_list(response['amp:amp_client_search']['record']):
                self.results.append(int(record['@id']))


class AllDevices(AirwavesAPIConnector):

    def __init__(self):
        super().__init__()

        response = self.get_XML('ap_list.xml')

        self.results = []

        if 'ap' in response['amp:amp_ap_search']:
            for record in self._ensure_list(response['amp:amp_ap_search']['ap']):
                self.results.append(int(record['@id']))
