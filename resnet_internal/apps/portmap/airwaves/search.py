"""
.. module:: resnet_internal.apps.portmap.airwaves.search
   :synopsis: Airwaves Search

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from urllib.parse import urlencode

from .connector import AirwavesAPIConnector


class DeviceQuery(AirwavesAPIConnector):

    def __init__(self, search_string):
        response = self.getXML('ap_search.xml?query=' + urlencode(search_string))

        self.results = []

        for record in response['amp:amp_ap_search']['record']:
            self.results.append(int(record['@id']))


class ClientQuery(AirwavesAPIConnector):

    def __init__(self, search_string):
        response = self.getXML('client_search.xml?query=' + urlencode(search_string))

        self.results = []

        for record in response['amp:amp_client_search']['record']:
            self.results.append(int(record['@id']))


class AllDevices(AirwavesAPIConnector):

    def __init__(self):
        response = self.getXML('ap_list.xml')

        self.results = []

        for record in response['amp:amp_ap_search']['ap']:
            self.results.append(int(record['@id']))
