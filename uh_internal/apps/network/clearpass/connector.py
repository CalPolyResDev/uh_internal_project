"""
.. module:: uh_internal.apps.network.clearpass.connector
   :synopsis: <Fill Me In!>

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from datetime import datetime
from urllib.parse import urljoin

from django.conf import settings
import requests
import xmltodict


class _APIConnector(object):
    _DATE_PATTERN = '%b %d, %Y %H:%M:%S %Z'

    def __init__(self, **kwargs):
        self.url = settings.CLEARPASS['url']
        self.username = settings.CLEARPASS['username']
        self.password = settings.CLEARPASS['password']
        self.verify = settings.CLEARPASS['verify_ssl']

        for k, v in kwargs:
            setattr(self, k, v)

    def process_response(self, response):
        if response.status_code != 200:
            raise Exception(response)

        return response.text

    def get(self, relative_url):
        url = urljoin(self.url, relative_url)
        response = requests.get(url, auth=(self.username, self.password))

        return self.process_response(response)

    def post(self, relative_url, headers, data):
        url = urljoin(self.url, relative_url)

        response = requests.post(url, headers=headers, data=data, auth=(self.username, self.password))

        return self.process_response(response)

    def get_XML(self, relative_url):
        response = self.get(relative_url)

        return xmltodict.parse(response)

    def post_XML(self, relative_url, xml):
        headers = {'Content-Type': 'application/xml'}
        response = self.post(relative_url, headers, xml)

        return xmltodict.parse(response)

    def _ensure_list(self, item):
        if not isinstance(item, list):
            item = [item]

        return item

    @classmethod
    def date_from_string(cls, string):
        return datetime.strptime(string, cls._DATE_PATTERN)
