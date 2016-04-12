"""
.. module:: uh_internal.apps.network.clearpass.configuration
   :synopsis: University Housing Internal ClearPass Configuration

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from urllib.parse import urlencode

from ..models import ClearPassLoginAttempt
from ..utils import mac_address_no_separator
from .exceptions import EndpointLookupError, APIError, MultipleEndpointError, EndpointUpdateError, EndpointUnknownOwnerError, EndpointInvalidOperationError
from .connector import _APIConnector


class Endpoint(_APIConnector):

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

        self.mac_vendor = endpoint_info.get('@macVendor', None)
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

    def update_endpoint(self, xml, error_message):
        response = self.post_XML('tipsapi/config/write/Endpoint', xml)

        if response['TipsApiResponse']['StatusCode'] != 'Success':
            raise EndpointUpdateError(error_message + ': ' + str(response))

    def get_username_of_owner(self):
        query = ClearPassLoginAttempt.objects.filter(client_mac_address=mac_address_no_separator(self.mac_address).lower())

        if query.exists():
            return query.first().username
        else:
            raise EndpointUnknownOwnerError('No known owner of device with mac: ' + self.mac_address)

    def set_to_known(self):
        xml = """
        <TipsApiRequest xmlns="http://www.avendasys.com/tipsapiDefs/1.0">
        <TipsHeader version="3.0"/>
        <Endpoints>
        <Endpoint status="Known" macAddress="{mac_address}"/>
        </Endpoints>
        </TipsApiRequest>""".format(mac_address=mac_address_no_separator(self.mac_address).lower())

        if self.status != "Known":
            self.update_endpoint(xml, 'Could not set endpoint to known')
        else:
            raise EndpointInvalidOperationError('Device is already known.')

    def add_tags(self, **kwargs):
        tag_xml = ''

        for key, value in kwargs.items():
            tag_template = '<EndpointTags tagName="{key}" tagValue="{value}"/>'
            tag_xml += tag_template.format(key=key, value=value)

        xml = """<TipsApiRequest xmlns="http://www.avendasys.com/tipsapiDefs/1.0">
        <TipsHeader version="3.0"/>
        <Endpoints>
        <Endpoint status="Known" macAddress="{mac_address}">
        {tags}
        </Endpoint>
        </Endpoints>
        </TipsApiRequest>""".format(mac_address=mac_address_no_separator(self.mac_address).lower(), tags=tag_xml)

        self.update_endpoint(xml, 'Could not add endpoint attributes: ' + str(kwargs))

    def add_os_type_override(self, os_type):
        tags = {
            'OS Type': os_type,
            'Username': self.get_username_of_owner(),
        }

        self.add_tags(**tags)

    def set_as_gaming_device(self):
        if not (self.profile and self.profile.get('category') == 'Game Console'):
            self.add_os_type_override('GAME')
        else:
            raise EndpointInvalidOperationError('Device is already profiled as a game console.')

    def set_as_gaming_pc(self):
        self.add_os_type_override('GAMING-PC')

    def set_as_media_device(self):
        if not (self.profile and self.profile.get('catgeory') == 'Home Audio/Video Equipment'):
            self.add_os_type_override('MEDIA')
        else:
            raise EndpointInvalidOperationError('Device is already profiled as a media device.')

    def remove_attribute(self, attribute_name):
        tags = {}
        for attribute in self.attributes:
            if attribute['name'] != attribute_name:
                tags[attribute['name']] = attribute['value']
            else:
                tags[attribute['name']] = ''

        self.add_tags(**tags)
