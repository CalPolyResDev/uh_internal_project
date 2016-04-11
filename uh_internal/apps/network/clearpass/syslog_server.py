"""
.. module:: uh_internal.apps.network.clearpass.syslog_server
   :synopsis: University Housing Internal ClearPass Syslog Server

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import logging
import socketserver
import queue as ThreadQueue

from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .parser import parse_login_attempts

logger = logging.getLogger(__name__)


def worker(packet_queue):
    while True:
        try:
            packet = packet_queue.get(True, 60)
        except ThreadQueue.Empty:
            pass

        if packet.get('shutdown', False):
            return

        parse_login_attempts(packet['data'])


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """Based on https://gist.github.com/marcelom/4218010"""

    def __init__(self, request, client_address, server, queue):
        self.queue = queue
        super().__init__(request, client_address, server)

    def handle(self):
        try:
            if self.client_address[0] in settings.CLEARPASS_SERVERS:
                data = bytes.decode(self.request[0].strip())
                self.queue.put({'data': data})
            else:
                logger.warning('Throwing away packet from ' + str(self.client_address[0]))
        except KeyboardInterrupt:
            print('Exiting...')
            self.queue.put({'shutdown': True})
            exit(0)
        except Exception as e:
            client.captureException()
            raise e
