"""
.. module:: resnet_internal.apps.core.models
   :synopsis: University Housing Internal Core Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging
import re

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models.base import Model
from django.db.models.fields import (CharField, IntegerField, TextField, DateTimeField, EmailField, NullBooleanField, BooleanField, GenericIPAddressField,
    URLField, SmallIntegerField)
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.http import urlquote
from ldap_groups.exceptions import InvalidGroupDN
from ldap_groups.groups import ADGroup as LDAPADGroup


logger = logging.getLogger(__name__)


class Community(Model):

    name = CharField(max_length=30, verbose_name="Community Name")

    def __str__(self):
        return self.name

    @cached_property
    def address(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Communities'


class Building(Model):

    name = CharField(max_length=30, verbose_name="Building Name")
    community = ForeignKey(Community, verbose_name="Community", related_name="buildings")

    def __str__(self):
        return self.name

    @cached_property
    def address(self):
        return self.community.address + ' ' + self.name


class Room(Model):

    name = CharField(max_length=10, verbose_name="Room Number")
    building = ForeignKey(Building, verbose_name="Building", related_name="rooms")

    def __str__(self):
        return self.name

    @cached_property
    def community(self):
        return self.building.community

    @cached_property
    def address(self):
        return self.building.address + ' ' + self.name

    def save(self, *args, **kwargs):
        # Upper name letters
        for field_name in ['name']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        super(Room, self).save(*args, **kwargs)


class Department(Model):

    name = CharField(max_length=50, verbose_name='Department Name')

    def __str__(self):
        return self.name


class SubDepartment(Model):

    name = CharField(max_length=50, verbose_name='Sub Department Name')
    department = ForeignKey(Department, verbose_name="Department", null=True, related_name="sub_departments")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sub Department'


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


class ADGroup(Model):
    distinguished_name = CharField(max_length=250, unique=True, verbose_name='Distinguished Name')
    display_name = CharField(max_length=50, verbose_name='Display Name')

    def clean(self):
        try:
            LDAPADGroup(self.distinguished_name).get_tree_members()
        except InvalidGroupDN:
            raise ValidationError('Invalid Group Distinguished Name. Please verify.')

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = 'AD Group'


class InternalUserManager(UserManager):

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()

        if not username:
            raise ValueError('The given username must be set.')

        email = self.normalize_email(email)
        username = self.normalize_email(username)

        user = self.model(username=username, email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser, last_login=now, **extra_fields)
        user.set_password("!")
        user.save(using=self._db)

        return user


class ResNetInternalUser(AbstractBaseUser, PermissionsMixin):
    """University Housing Internal User Model"""

    username = CharField(max_length=30, unique=True, verbose_name='Username')
    first_name = CharField(max_length=30, blank=True, verbose_name='First Name')
    last_name = CharField(max_length=30, blank=True, verbose_name='Last Name')
    email = EmailField(blank=True, verbose_name='Email Address')
    ad_groups = ManyToManyField(ADGroup)

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = 'username'
    objects = InternalUserManager()

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
    is_developer = BooleanField(default=False)  # full access to University Housing Internal

    # RLIN Legacy flags
    is_csd = BooleanField(default=False)
    is_ral = BooleanField(default=False)
    is_ral_manager = BooleanField(default=False)
    is_ra = BooleanField(default=False)
    is_fd_staff = BooleanField(default=False)

    #
    # A set of flags that keeps a record of each user's orientation progress.
    #
    onity_complete = BooleanField(default=False)  # Onity Door access
    srs_complete = BooleanField(default=False)  # SRS Manager access
    payroll_complete = BooleanField(default=False)  # Payroll access
    orientation_complete = BooleanField(default=False)  # Promotes user to Technicain status

    class Meta:
        verbose_name = 'University Housing Internal User'

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


class TechFlair(Model):
    """A mapping of users to custom flair."""

    tech = ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Technician')
    flair = CharField(max_length=30, unique=True, verbose_name='Flair')

    class Meta:
        verbose_name = 'Tech Flair'
        verbose_name_plural = 'Tech Flair'


class NavbarLink(Model):
    display_name = CharField(max_length=50, verbose_name='Display Name')
    groups = ManyToManyField(ADGroup, verbose_name='AD Groups')
    icon = CharField(max_length=100, verbose_name='Icon Static File Location', blank=True, null=True)
    sequence_index = SmallIntegerField(verbose_name='Sequence Index')
    parent_group = ForeignKey('NavbarLink', related_name='links', blank=True, null=True, verbose_name='Parent Link Group')

    external_url = URLField(verbose_name='URL', blank=True, null=True)
    url_name = CharField(max_length=100, blank=True, null=True)
    onclick = CharField(max_length=200, blank=True, null=True, verbose_name='Onclick Handler')

    def __str__(self):
        return self.display_name

    def clean(self):
        if self.url_name and self.external_url:
            raise ValidationError('Navbar Links should have either a url name or an external url, not both.')

        if self.url_name:
            try:
                reverse(self.url_name)
            except NoReverseMatch:
                raise ValidationError('URL Name could not be resolved. Please enter a valid URL Name.')

    @cached_property
    def url(self):
        url = ''

        if self.url_name:
            try:
                url = reverse(self.url_name)
            except NoReverseMatch:
                logger.warning('Could not resolve ``' + self.url_name + '`` for navbar link ' + self.display_name)
                pass
        else:
            url = self.external_url

        return url

    @cached_property
    def is_link_group(self):
        return NavbarLink.objects.filter(parent_group__id=self.id).exists()

    @cached_property
    def html_id(self):
        return self.display_name.lower().replace(' ', '_')

    @cached_property
    def target(self):
        return '_blank' if self.external_url else '_self'
