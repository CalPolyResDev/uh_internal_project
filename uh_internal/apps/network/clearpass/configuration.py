"""
.. module:: uh_internal.apps.network.clearpass.configuration
   :synopsis: University Housing Internal ClearPass Configuration

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from datetime import datetime
from urllib.parse import urljoin, urlencode

from django.conf import settings
import requests
import xmltodict

from ..utils import mac_address_no_separator


class Error(Exception):
    pass


class APIError(Error):
    """Exception raised when an API request fails."""
    pass


class EndpointLookupError(Error):
    """Exception raised when an endpoint can't be found."""
    pass


class MultipleEndpointError(Error):
    """Exception raised when multiple endpoints are returned
    and 1 was expected."""

    pass


class _APIConnectorMixin(object):
    _DATE_PATTERN = '%b %d, %Y %H:%M:%S %Z'

    def __init__(self, **kwargs):
        self.url = settings.CLEARPASS['url']
        self.username = settings.CLEARPASS['username']
        self.password = settings.CLEARPASS['password']
        self.verify = settings.CLEARPASS['verify_ssl']

        for k, v in kwargs:
            setattr(self, k, v)

    def get(self, relative_url):
        url = urljoin(self.url, relative_url)
        response = requests.get(url, auth=(self.username, self.password))

        if response.status_code != 200:
            raise Exception(response)

        return response.text

    def get_XML(self, relative_url):
        response = self.get(relative_url)

        return xmltodict.parse(response)

    def _ensure_list(self, item):
        if not isinstance(item, list):
            item = [item]

        return item

    @classmethod
    def date_from_string(cls, string):
        return datetime.strptime(string, cls._DATE_PATTERN)


class Endpoint(_APIConnectorMixin):

    def __init__(self, mac_address, **kwargs):
        super().__init__(**kwargs)

        mac_address = mac_address_no_separator(mac_address).lower()

        xml_response = self.get_XML('tipsapi/config/read/Endpoint/equals?' + urlencode({'macAddress': mac_address}))

        if xml_response['TipsApiResponse']['StatusCode'] != 'Success':
            raise APIError('ClearPass API Error: ' + str(xml_response))

        endpoint_count = int(xml_response['TipsApiResponse']['EntityMaxRecordCount'])

        if endpoint_count == 0:
            raise EndpointLookupError(xml_response)
        elif endpoint_count > 1:
            raise MultipleEndpointError('MAC Address is not Unique: ' + str(xml_response))

        endpoint_info = xml_response['TipsApiResponse']['Endpoints']['Endpoint']

        self.mac_vendor = endpoint_info['@macVendor']
        self.mac_address = mac_address
        self.status = endpoint_info['@status']

        self.profile = None

        if 'EndpointProfile' in endpoint_info:
            endpoint_profile = endpoint_info['EndpointProfile']
            self.profile = {}

            self.profile['date_updated'] = self.date_from_string(endpoint_profile['@updatedAt'])
            self.profile['date_added'] = self.date_from_string(endpoint_profile['@addedAt'])
            self.profile['fingerprint'] = endpoint_profile['@fingerprint']
            self.profile['conflict'] = False if endpoint_profile['@conflict'] == 'false' else True
            self.profile['device_name'] = endpoint_profile['@name']
            self.profile['family'] = endpoint_profile['@family']
            self.profile['category'] = endpoint_profile['@category']
            self.profile['ip_address'] = endpoint_profile['@ipAddress']
            self.profile['hostname'] = endpoint_profile['@hostname']

        self.attributes = None

        if 'EndpointTags' in endpoint_info:
            self.attributes = []
            endpoint_tags = self._ensure_list(endpoint_info['EndpointTags'])

            for tag_info in endpoint_tags:
                attribute = {
                    'name': tag_info['@tagName'],
                    'value': tag_info['@tagValue'],
                }
                self.attributes.append(attribute)
