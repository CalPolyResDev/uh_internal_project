"""
.. module:: uh_internal.apps.network.clearpass.syslog_server
   :synopsis: University Housing Internal ClearPass Syslog Server

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import socketserver

from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .parser import parse_login_attempts


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """Based on https://gist.github.com/marcelom/4218010"""

    def handle(self):
        try:
            if self.client_address[0] in settings.CLEARPASS_SERVERS:
                data = bytes.decode(self.request[0].strip())
                parse_login_attempts(data)
        except KeyboardInterrupt:
            print('Exiting...')
            exit(0)
        except Exception as e:
            client.captureException()
            raise e
