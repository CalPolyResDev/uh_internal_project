"""
.. module:: resnet_internal.apps.portmap.airwaves.connector
   :synopsis: Airwaves Connector

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from datetime import datetime
from urllib.parse import urljoin
import json

from django.conf import settings
from django.utils.encoding import smart_text
import requests
import urllib3
import xmltodict


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
AIRWAVES_XML_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class AirwavesAPIConnector(object):
    session = None

    def __init__(self, **kwargs):
        self.url = settings.AIRWAVES['url']
        self.username = settings.AIRWAVES['username']
        self.password = settings.AIRWAVES['password']
        self.verify = settings.AIRWAVES['verify_ssl']

        for k, v in kwargs:
            setattr(self, k, v)

    def login(self):
        response = AirwavesAPIConnector.session.post(urljoin(self.url, '/LOGIN'),
                                                     data={'credential_0': self.username,
                                                           'credential_1': self.password,
                                                           'destination': '/',
                                                           'login': 'Log In'})

        AirwavesAPIConnector.session.headers.update({'X-BISCOTTI': response.headers['X-BISCOTTI']})

    def connect(self):
        AirwavesAPIConnector.session = requests.Session()
        AirwavesAPIConnector.session.verify = self.verify
        self.login()

    def get(self, relative_url):
        def perform_request():
            return AirwavesAPIConnector.session.get(urljoin(self.url, relative_url))

        if not AirwavesAPIConnector.session:
            self.connect()

        response = perform_request()

        if response.status_code == 403:
            self.login()
            response = perform_request()

        if response.status_code != 200:
            raise Exception(response)

        return smart_text(response.content)

    def get_JSON(self, relative_url):
        response = self.get(relative_url)

        return json.loads(smart_text(response))

    def get_XML(self, relative_url):
        response = self.get(relative_url)

        response = ''.join(response.splitlines(True)[1:])  # Delete first line

        return xmltodict.parse(response)

    def datetime_from_xml_date(self, xml_date):
        xml_date = ''.join(xml_date.rsplit(':', 1))
        return datetime.strptime(xml_date, AIRWAVES_XML_DATE_FORMAT)

    def _ensure_list(self, item):
        if not isinstance(item, list):
            item = [item]

        return item
