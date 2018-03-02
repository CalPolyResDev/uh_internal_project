"""
.. module:: resnet_internal.apps.dailyduties.models
   :synopsis: University Housing Internal Daily Duty Models.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from datetime import datetime, timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Model, ForeignKey
from django.db.models.deletion import SET_NULL
from django.db.models.fields import CharField, DateTimeField, TextField, EmailField, SlugField, IntegerField, BooleanField
from django.utils.functional import cached_property

from ..core.models import UHInternalUser
from ..core.utils import unique_slugify


class DailyDuties(Model):
    """Daily Duties Information"""

    name = CharField(max_length=15, unique=True, verbose_name='Duty Name')
    last_checked = DateTimeField(verbose_name='Last DateTime Checked')
    last_user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Last User to Check', on_delete=SET_NULL, null=True, blank=True)

    class Meta(object):
        verbose_name_plural = 'Daily Duties'
        verbose_name = 'Daily Duty'
