"""
.. module:: resnet_internal.apps.portmap.airwaves.data
   :synopsis: Airwaves Data

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from datetime import datetime
from urllib.parse import urlencode

from pytz import timezone

from .connector import AirwavesAPIConnector


class OverallStatistics(AirwavesAPIConnector):

    def __init__(self):
        super().__init__()

        response = self.get_JSON('amp_stats.json')

        self.up = {}
        self.up['access_points'] = int(response['up']['tooltip']['thin'])
        self.up['controllers'] = int(response['up']['tooltip']['controller'])
        self.up['switches'] = int(response['up']['tooltip']['router'])

        self.down = {}
        self.down['access_points'] = int(response['down']['tooltip']['thin'])
        self.down['controllers'] = int(response['down']['tooltip']['controller'])
        self.down['switches'] = int(response['down']['tooltip']['router'])

        self.clients = int(response['client_count']['count'])


class APClientInfo(AirwavesAPIConnector):

    def __init__(self, ap_id):
        super().__init__()

        response = self.get_JSON('/api/list_view.json?list=client_of_device&fv_id=0&ap_id=' + str(ap_id))

        self.clients = []

        for record in response['records']:
            client_info = {
                'connect_time': datetime.fromtimestamp(record['connect_time']['value'], timezone('US/Pacific')),
                'snr': record['snr']['value'],  # dB?
                'mac_address': record['mac']['mac'],
                'role': record['role']['value'],
                'username': record['username']['value'],  # Sometimes an email address, sometimes not >:(
            }

            self.clients.append(client_info)


class DeviceInfo(AirwavesAPIConnector):

    def __init__(self, ap_id):
        super().__init__()

        response_detail = self.get_XML('ap_detail.xml?id=' + str(ap_id))
        response_list = self.get_XML('ap_list.xml?id=' + str(ap_id))

        device_detail = response_detail['amp:amp_ap_detail']['ap']
        device_list = response_list['amp:amp_ap_list']['ap']

        print(device_detail)

        self.ap_folder = device_detail['ap_folder']
        self.device_type = device_detail['ap_group']
        self.up = True if device_detail['is_up'] == 'true' else False
        self.uptime = device_detail['snmp_uptime']

        self.radios = []

        if 'radio' in device_detail:
            for radio in self._ensure_list(device_detail['radio']):
                radio_info = {
                    'index': radio['@index'],
                    'bssids': [],
                    'clients': [],
                    'operational_mode': radio['operational_mode'],
                    'interface': radio['radio_interface'],
                    'type': radio['radio_type'],
                }

                if 'client' in radio:
                    for client in self._ensure_list(radio['client']):
                        client_info = {
                            'associated': True if client['assoc_stat'] == 'true' else False,
                            'authenticated': True if client['auth_stat'] == 'true' else False,
                            'mac_address': client['radio_mac'],
                            'signal': client['signal'],
                            'snr': client['snr'],
                        }

                        radio_info['clients'].append(client_info)

                if 'bssid' in radio:
                    for bssid in self._ensure_list(radio['bssid']):
                        radio_info['bssids'].append(bssid)

                self.radios.append(radio_info)

        self.interfaces = []

        if 'interface' in device_detail:
            for interface in self._ensure_list(device_detail['interface']):
                interface_info = {
                    'enabled': True if interface['admin_status'] == 'Up' else False,
                    'name': interface['name'],
                    'mac_address': interface['mac_address'],
                    'connected': True if interface['oper_status'] == 'Up' else False,
                }
                self.interfaces.append(interface_info)

        self.client_count = device_list['client_count']
        self.controller_id = device_list['controller_id']
        self.firmware = device_list['firmware']
        self.ip_address = device_list['lan_ip']
        self.mac_address = device_list['lan_mac']
        self.last_contacted = datetime.fromtimestamp(int(device_list['last_contacted']))
        self.last_reboot = datetime.fromtimestamp(int(device_list['last_reboot']))
        self.manufacturer = device_list['mfgr']
        self.model = device_list['model']['#text']
        self.monitor_only = True if device_list['monitor_only'] == 'true' else False
        self.name = device_list['name']
        self.serial_number = device_list['serial_number']

        if 'radio' in device_list:
            for radio in self._ensure_list(device_list['radio']):
                if self.radios:
                    for detail_radio in self.radios:
                        if detail_radio['index'] == radio['@index']:
                            detail_radio['channel'] = radio['channel']
                            detail_radio['enabled'] = True if radio['enabled'] == 'true' else False
                            detail_radio['mac_address'] = radio['radio_mac']
                            detail_radio['transmit_power'] = radio['transmit_power']

                            break


class ClientInfo(AirwavesAPIConnector):

    def __init__(self, client_mac):
        super().__init__()

        response = self.get_XML('client_detail.xml?' + urlencode({'mac': client_mac}))

        client = response['amp:amp_client_detail']['client']

        if 'ap' in client:
            self.ap_id = client['ap']['@id']
            self.ap_name = client['ap']['#text']
        else:
            self.ap_id = None
            self.ap_name = None

        self.mac_address = client['@mac']

        self.associations = []

        if 'association' in client:
            for association in self._ensure_list(client['association']):
                association_info = {
                    'ap_id': association['ap']['@id'],
                    'bytes_used': association['bytes_used'],
                    'connect_time': self.datetime_from_xml_date(association['connect_time']),
                    'disconnect_time': self.datetime_from_xml_date(association['disconnect_time']),
                    'ip_addresses': [],
                    'rssi': int(association['rssi']) if 'rssi' in association else None,
                }

                if 'lan_elements' in association:
                    for lan in self._ensure_list(association['lan_elements']['lan']):
                        association_info['ip_addresses'].append(lan['@ip_address'])

                self.associations.append(association_info)
