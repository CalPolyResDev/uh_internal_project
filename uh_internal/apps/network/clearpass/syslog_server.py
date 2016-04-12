"""
.. module:: uh_internal.apps.network.clearpass.syslog_server
   :synopsis: University Housing Internal ClearPass Syslog Server

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import logging
import queue as ThreadQueue
import socket
import socketserver

from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .parser import parse_login_attempts


logger = logging.getLogger(__name__)


def packet_processing_worker(packet_queue):
    while True:
        try:
            packet = packet_queue.get(True, 60)
        except ThreadQueue.Empty:
            continue

        if packet.get('shutdown', False):
            return

        parse_login_attempts(packet['data'])


class QueuingSyslogUDPHandler(socketserver.BaseRequestHandler):
    """ Based on https://gist.github.com/marcelom/4218010

        Adapted to a Producer-Consumer Architecture to avoid
        dropped UDP packets.
    """

    def __init__(self, request, client_address, server):
        self.queue = server.queue
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


class QueuingUDPServer(socketserver.UDPServer):
    request_queue_size = 5000
    max_packet_size = 30000

    def __init__(self, server_address, RequestHandlerClass, queue, **kwargs):
        super().__init__(server_address, RequestHandlerClass, **kwargs)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 10)  # 10 MB
        self.queue = queue
