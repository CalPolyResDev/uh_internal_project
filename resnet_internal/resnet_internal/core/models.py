"""
.. module:: resnet_internal.core.models
   :synopsis: ResNet Internal Core Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import re

from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.conf import settings
from django.db.models import Model, CharField, IntegerField, TextField, DateTimeField, ForeignKey, EmailField, NullBooleanField, BooleanField
from django.utils.http import urlquote
from django.core.mail import send_mail


class Community(Model):
    """Housing Community."""

    name = CharField(max_length=30, verbose_name="Community Name")

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'community'
        managed = False
        verbose_name = u'Community'
        verbose_name_plural = u'Communities'


class Building(Model):
    """Housing Building."""

    name = CharField(max_length=30, verbose_name="Building Name")
    community = ForeignKey(Community, verbose_name="Community")

    def __unicode__(self):
        return str(self.community) + " " + self.name

    class Meta:
        db_table = u'building'
        managed = False
        verbose_name = u'Building'


class DailyDuties(Model):
    """Daily Duties Information"""

    name = CharField(max_length=15, unique=True, verbose_name='Duty Name')
    last_checked = DateTimeField(verbose_name='Last DateTime Checked')
    last_user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Last User to Check')


class SiteAnnouncements(Model):
    """Latest site announcements"""

    title = CharField(max_length=150, verbose_name='Title')
    description = TextField(verbose_name='Description')
    created = DateTimeField(verbose_name='Entry Creation Date')

    class Meta:
        get_latest_by = "created"
        verbose_name = u'Site Announcement'


class StaffMapping(Model):
    """A mapping of various department staff to their respective positions."""

    staff_title = CharField(max_length=35, unique=True, verbose_name=u'Staff Title')
    staff_name = CharField(max_length=50, verbose_name=u'Staff Full Name')
    staff_alias = CharField(max_length=8, verbose_name=u'Staff Alias')
    staff_ext = IntegerField(max_length=4, verbose_name=u'Staff Telephone Extension')

    class Meta:
        db_table = u'staffmapping'
        managed = False
        verbose_name = u'Campus Staff Mapping'


class ResNetInternalUser(AbstractBaseUser, PermissionsMixin):
    """ResNet Internal User Model"""

    username = CharField(max_length=30, unique=True, verbose_name=u'Username')
    first_name = CharField(max_length=30, blank=True, verbose_name=u'First Name')
    last_name = CharField(max_length=30, blank=True, verbose_name=u'Last Name')
    email = EmailField(blank=True, verbose_name=u'Email Address')

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    #
    # A set of flags for each user that decides what the user can and cannot see.
    # Flags are determined by which tools a user needs to fill his/her job description.
    #
    is_new_tech = NullBooleanField(null=True)  # determines whether or not to show the orentation site
    is_net_admin = BooleanField(default=False)  # limited access only to apps that network admins are allowed to use
    is_telecom = BooleanField(default=False)  # limited access only to apps that telecom admins are allowed to use
    is_tag = BooleanField(default=False)  # limited access only to apps that uh-tag mambers are allowed to use
    is_tag_readonly = BooleanField(default=False)  # limited access only to apps that uh-tag mambers are allowed to use (read-only permissions)
    is_technician = BooleanField(default=False)  # access to technician tools
    is_rn_staff = BooleanField(default=False)  # access to all tools as well as staff tools
    is_developer = BooleanField(default=False)  # full access to resnet internal

    #
    # A set of flags that keeps a record of each user's orientation progress.
    #
    onity_complete = BooleanField(default=False)  # Onity Door access
    srs_complete = BooleanField(default=False)  # SRS Manager access
    payroll_complete = BooleanField(default=False)  # Payroll access
    orientation_complete = BooleanField(default=False)  # Promotes user to Technicain status

    #
    # Preferences
    #
    open_links_in_frame = BooleanField(default=False)  # Link handling

    class Meta:
        verbose_name = u'ResNet Internal User'

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """Returns the first_name combined with the last_name separated via space with the possible '- ADMIN' removed."""

        full_name = '%s %s' % (self.first_name, re.sub(r' - ADMIN', '', self.last_name))
        return full_name.strip()

    def get_alias(self):
        """Returns the username with the possible '-admin' removed."""

        return re.sub(r'-admin', '', self.username)

    def get_short_name(self):
        "Returns the short name for the user."

        return self.get_alias()

    def email_user(self, subject, message, from_email=None):
        """Sends an email to this user."""

        send_mail(subject, message, from_email, [self.email])
