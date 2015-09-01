"""
.. module:: resnet_internal.apps.dailyduties.models
   :synopsis: ResNet Internal Daily Duty Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings
from django.db.models import Model, ForeignKey
from django.db.models.deletion import SET_NULL
from django.db.models.fields import CharField, DateTimeField


class DailyDuties(Model):
    """Daily Duties Information"""

    name = CharField(max_length=15, unique=True, verbose_name='Duty Name')
    last_checked = DateTimeField(verbose_name='Last DateTime Checked')
    last_user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Last User to Check', on_delete=SET_NULL, null=True, blank=True)

    class Meta(object):
        verbose_name_plural = 'Daily Duties'
        verbose_name = 'Daily Duty'
