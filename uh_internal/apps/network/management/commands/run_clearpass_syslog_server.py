"""
.. module:: uh_internal.apps.network.management.commands.run_clearpass_syslog_server
   :synopsis: University Housing Internal Clearpass Syslog Server Run Command

   Requires that port 514 be forwarded to 5140.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
import socketserver

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        from ...clearpass.syslog_server import SyslogUDPHandler  # noqa

        server = socketserver.UDPServer(('0.0.0.0', 5140), SyslogUDPHandler)
        server.serve_forever()
