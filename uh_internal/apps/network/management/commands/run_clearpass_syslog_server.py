"""
.. module:: uh_internal.apps.network.management.commands.run_clearpass_syslog_server
   :synopsis: University Housing Internal Clearpass Syslog Server Run Command

   Requires that port 514 be forwarded to 5140.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from multiprocessing import Queue, Process
import socketserver

from django.core.management.base import BaseCommand
from django.db import connection


class LargePacketUDPServer(socketserver.UDPServer):
    request_queue_size = 5000
    max_packet_size = 30000

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.queue = kwargs['queue']

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self, self.queue)


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        from ...clearpass.syslog_server import SyslogUDPHandler, worker  # noqa
        queue = Queue(2000)
        worker_process = Process(target=worker, args=(queue,))
        connection.close()
        worker_process.start()

        server = LargePacketUDPServer(('0.0.0.0', 5140), SyslogUDPHandler, queue=queue)
        server.serve_forever()
