"""
.. module:: resnet_internal.apps.dailyduties.models
   :synopsis: ResNet Internal Daily Duty Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings
from django.db.models import Model, ForeignKey
from django.db.models.fields import CharField, DateTimeField, DateField


class DailyDuties(Model):
    """Daily Duties Information"""

    name = CharField(max_length=15, unique=True, verbose_name='Duty Name')
    last_checked = DateTimeField(verbose_name='Last DateTime Checked')
    last_user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Last User to Check')


class VoicemailMessage(Model):
    uuid = CharField(max_length=100, unique=True, verbose_name='IMAP UUID')
    sender = CharField(max_length=100, verbose_name='Sender')
    date = DateTimeField(verbose_name='Date Received')
