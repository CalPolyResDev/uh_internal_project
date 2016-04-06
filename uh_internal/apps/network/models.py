"""
.. module:: resnet_internal.apps.network.models
   :synopsis: University Housing Internal Network Models.

   Major credit to Kyle Fast for saving a couple months' worth of work entering database info.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: Thomas Willson <thomas.willson@me.com>


"""

from django.contrib.postgres.fields.array import ArrayField
from django.db.models.base import Model
from django.db.models.fields import CharField, GenericIPAddressField, BooleanField, PositiveSmallIntegerField, IntegerField,\
    DateTimeField, TextField
from django.db.models.fields.related import ForeignKey
from django.utils.functional import cached_property

from ..computers.fields import MACAddressField
from ..core.models import Room


class NetworkDevice(Model):
    """Network Device"""

    display_name = CharField(max_length=100, verbose_name='Display Name')
    dns_name = CharField(max_length=75, verbose_name='DNS Name', null=True, blank=True)
    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address', null=True, blank=True)
    mac_address = MACAddressField(verbose_name='MAC Address', null=True, blank=True)
    upstream_device = ForeignKey('NetworkDevice', related_name='downstream_devices', null=True, blank=True)
    room = ForeignKey(Room, verbose_name='Room', null=True, blank=True)
    airwaves_id = IntegerField(null=True, blank=True)

    def __str__(self):
        return self.display_name

    @cached_property
    def building(self):
        try:
            return self.room.building
        except AttributeError:
            return None

    @cached_property
    def community(self):
        try:
            return self.room.building.community
        except AttributeError:
            return None


class Port(NetworkDevice):

    blade_number = PositiveSmallIntegerField(verbose_name='Blade')
    port_number = PositiveSmallIntegerField(verbose_name='Port')
    active = BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return self.jack

    @cached_property
    def jack(self):
        return self.display_name

    @cached_property
    def switch_ip(self):
        return self.upstream_device.ip_address

    @cached_property
    def switch_name(self):
        return self.upstream_device.display_name

    def save(self, *args, **kwargs):
        # Upper jack letters
        for field_name in ['jack']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        super(Port, self).save(*args, **kwargs)


AP_TYPES = ['5 Ghz', '2.4 Ghz', 'Air Monitor']
AP_TYPE_CHOICES = [(AP_TYPES.index(ap_type), ap_type) for ap_type in AP_TYPES]


class AccessPoint(NetworkDevice):
    """Access Point"""

    property_id = CharField(max_length=7, unique=True, verbose_name='Property ID')
    serial_number = CharField(max_length=9, unique=True, verbose_name='Serial Number')
    ap_type = PositiveSmallIntegerField(choices=AP_TYPE_CHOICES, verbose_name='Type')


class NetworkInfrastructureDevice(NetworkDevice):
    """Network Infrastructure Device."""

    pass


class ClearPassLoginAttempt(Model):
    ACCEPT_RESULT = 0
    REJECT_RESULT = 1
    TIMEOUT_RESULT = 2

    RESULT_CHOICES = (
        (ACCEPT_RESULT, 'ACCEPT'),
        (REJECT_RESULT, 'REJECT'),
        (TIMEOUT_RESULT, 'TIMEOUT'),
    )

    username = CharField(max_length=50, blank=True, null=True)
    time = DateTimeField()
    service = CharField(max_length=100)
    roles = ArrayField(CharField(max_length=50))
    client_mac_address = MACAddressField()
    enforcement_profiles = ArrayField(CharField(max_length=100))
    result = PositiveSmallIntegerField(choices=RESULT_CHOICES)
    clearpass_ip = GenericIPAddressField()
    alerts = TextField(null=True, blank=True)

    def __str__(self):
        return 'Username: ' + str(self.username) + ', Service: ' + str(self.service) + ', Roles: ' + str(self.roles) + '\n'

    @cached_property
    def client_mac_address_formatted(self):
        from .utils import mac_address_with_colons  # noqa
        return mac_address_with_colons(self.client_mac_address)

    class Meta:
        verbose_name = 'ClearPass Login Attempt'
