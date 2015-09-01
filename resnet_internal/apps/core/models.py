"""
.. module:: resnet_internal.apps.core.models
   :synopsis: ResNet Internal Core Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import re

from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db.models.base import Model
from django.db.models.fields import CharField, IntegerField, TextField, DateTimeField, EmailField, NullBooleanField, BooleanField, GenericIPAddressField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.http import urlquote
from django.core.mail import send_mail


class Community(Model):
    """University Housing Community."""

    name = CharField(max_length=30, verbose_name="Community Name")
    buildings = ManyToManyField("Building")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'University Housing Community'
        verbose_name_plural = 'University Housing Communities'


class Building(Model):
    """University Housing Building."""

    name = CharField(max_length=30, verbose_name="Building Name")
    community = ForeignKey(Community, verbose_name="Community", related_name="buildings")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'University Housing Building'


class SubDepartment(Model):
    """University Housing Sub Departments."""

    name = CharField(max_length=50, verbose_name='Sub Department Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'University Housing Sub Department'


class Department(Model):
    """University Housing Departments."""

    name = CharField(max_length=50, verbose_name='Department Name')
    sub_departments = ManyToManyField(SubDepartment)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'University Housing Department'


class NetworkDevice(Model):
    """Network Infrastructure Device."""
    
    display_name = CharField(max_length=100, verbose_name='Display Name')
    dns_name = CharField(max_length=75, verbose_name='DNS Name')
    ip_address = GenericIPAddressField(verbose_name='IP Address', protocol='IPv4')


class SiteAnnouncements(Model):
    """Latest site announcements"""

    title = CharField(max_length=150, verbose_name='Title')
    description = TextField(verbose_name='Description')
    created = DateTimeField(verbose_name='Entry Creation Date')

    class Meta:
        get_latest_by = "created"
        verbose_name = 'Site Announcement'


class StaffMapping(Model):
    """A mapping of various department staff to their respective positions."""

    staff_title = CharField(max_length=35, unique=True, verbose_name='Staff Title')
    staff_name = CharField(max_length=50, verbose_name='Staff Full Name')
    staff_alias = CharField(max_length=8, verbose_name='Staff Alias')
    staff_ext = IntegerField(verbose_name='Staff Telephone Extension')

    class Meta:
        db_table = 'staffmapping'
        managed = False
        verbose_name = 'Campus Staff Mapping'


class TechFlair(Model):
    """A mapping of users to custom flair."""

    tech = ForeignKey("ResNetInternalUser", verbose_name='Technician')
    flair = CharField(max_length=30, unique=True, verbose_name='Flair')

    class Meta:
        verbose_name = 'Tech Flair'
        verbose_name_plural = 'Tech Flair'


class ResNetInternalUser(AbstractBaseUser, PermissionsMixin):
    """ResNet Internal User Model"""

    username = CharField(max_length=30, unique=True, verbose_name='Username')
    first_name = CharField(max_length=30, blank=True, verbose_name='First Name')
    last_name = CharField(max_length=30, blank=True, verbose_name='Last Name')
    email = EmailField(blank=True, verbose_name='Email Address')

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
        verbose_name = 'ResNet Internal User'

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
