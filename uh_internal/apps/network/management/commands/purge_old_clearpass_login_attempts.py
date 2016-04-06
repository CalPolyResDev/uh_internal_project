"""
.. module:: uh_internal.apps.network.management.commands.purge_old_clearpass_login_attempts
   :synopsis: University Housing Internal Clearpass Login Attempt Cleaner

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
import datetime

from django.core.management.base import BaseCommand

from ...models import ClearPassLoginAttempt


class Command(BaseCommand):

    def handle(self, *args, **options):
        ClearPassLoginAttempt.objects.filter(time__lt=datetime.datetime.now() - datetime.timedelta(days=14)).delete()
