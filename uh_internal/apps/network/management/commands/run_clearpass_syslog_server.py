"""
.. module:: uh_internal.apps.network.management.commands.run_clearpass_syslog_server
   :synopsis: University Housing Internal Clearpass Syslog Server Run Command

   Requires that port 514 be forwarded to 5140.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from multiprocessing import Queue, Process

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        from ...clearpass.syslog_server import QueuingSyslogUDPHandler, QueuingUDPServer, packet_processing_worker  # noqa

        queue = Queue(10000)

        worker_process = Process(target=packet_processing_worker, args=(queue,))
        connection.close()  # Close Django DB connection before forking
        worker_process.start()

        server = QueuingUDPServer(('0.0.0.0', 5140), QueuingSyslogUDPHandler, queue)
        server.serve_forever(poll_interval=0.05)
