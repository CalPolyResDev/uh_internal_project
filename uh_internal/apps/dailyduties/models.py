"""
.. module:: resnet_internal.apps.dailyduties.models
   :synopsis: University Housing Internal Daily Duty Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import datetime, timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Model, ForeignKey
from django.db.models.deletion import SET_NULL
from django.db.models.fields import CharField, DateTimeField, TextField, EmailField, SlugField, IntegerField
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


class EmailPermalink(Model):
    current_mailbox = CharField(max_length=100)
    current_uid = IntegerField()

    date = DateTimeField()
    subject = TextField()
    sender_name = CharField(max_length=255)
    sender_email = EmailField()

    slug = SlugField(unique=True, blank=True)

    def _generate_slug(self):
        if not self.slug:
            slug_str = self.sender_email + ' ' + self.subject
            unique_slugify(self, slug_str)

    def save(self, **kwargs):
        self._generate_slug()
        super().save(**kwargs)

    @cached_property
    def absolute_uri(self):
        self._generate_slug()

        return urljoin(settings.DEFAULT_BASE_URL, reverse('dailyduties:email_permalink_view_message', kwargs={'slug': self.slug}))


class EmailViewingRecord(Model):
    mailbox = CharField(max_length=100)
    uid = IntegerField()

    expiry_time = DateTimeField()
    user = ForeignKey(UHInternalUser)

    def save(self, **kwargs):
        self.expiry_time = datetime.now() + timedelta(seconds=30)
