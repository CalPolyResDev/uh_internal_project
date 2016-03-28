"""
.. module:: resnet_internal.apps.computers.models
   :synopsis: University Housing Internal Computer Index Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models.base import Model
from django.db.models.fields import BooleanField, CharField, IntegerField, GenericIPAddressField, DateField
from django.db.models.fields.related import ForeignKey
from srsconnector.models import PinholeRequest, DomainNameRequest

from ..core.models import Department, SubDepartment
from ..portmap.models import NetworkDevice
from .fields import ListField


class Computer(NetworkDevice):

    department = ForeignKey(Department, verbose_name='Department')
    sub_department = ForeignKey(SubDepartment, verbose_name='Sub Department')

    model = CharField(max_length=25, verbose_name='Model')
    serial_number = CharField(max_length=20, verbose_name='Serial Number', blank=True, null=True, unique=True, default=None)
    property_id = CharField(max_length=50, verbose_name='Cal Poly Property ID', blank=True, null=True, unique=True, default=None)
    location = CharField(max_length=100, verbose_name='Location', blank=True, null=True)
    date_purchased = DateField(verbose_name='Date Purchased')
    dn = CharField(max_length=250, verbose_name='Distinguished Name')
    description = CharField(max_length=100, verbose_name='Description')

    dhcp = BooleanField(default=False)

    def __str__(self):
        return self.computer_name

    def save(self, *args, **kwargs):
        """Uppercase field names on save."""

        for field_name in ['computer_name', 'mac_address', 'serial_number', 'property_id']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        for field_name in ['serial_number', 'property_id']:
            value = getattr(self, field_name, None)
            if not value:
                setattr(self, field_name, None)

        if not self.ip_address:
            self.ip_address = None
            self.dhcp = True
        else:
            self.dhcp = False

        if self.dhcp:
            self.ip_address = None

        super(Computer, self).save(*args, **kwargs)


class Pinhole(Model):
    """Firewall Pinholes."""

    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')
    service_name = CharField(max_length=50, verbose_name='Service Name')
    inner_fw = BooleanField(default=None, verbose_name='Inner Firewall')
    border_fw = BooleanField(default=None, verbose_name='Border Firewall')
    tcp_ports = ListField(verbose_name='TCP Ports')
    udp_ports = ListField(verbose_name='UDP Ports')
    sr_number = IntegerField(null=True, verbose_name='SR Number', db_column='ticket_id')

    def __str__(self):
        return 'Pinhole: ' + str(self.ip_address)

    @property
    def pinhole_request(self):
        if self.sr_number:
            return PinholeRequest.objects.get(ticket_id=self.sr_number)
        return None


class DomainName(Model):
    """Domain Names."""

    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')
    domain_name = CharField(max_length=100, verbose_name='Domain Name')
    sr_number = IntegerField(null=True, verbose_name='SR Number', db_column='ticket_id')

    def __str__(self):
        return 'DNS Record: ' + str(self.ip_address)

    @property
    def domain_name_request(self):
        if self.sr_number:
            return DomainNameRequest.objects.get(ticket_id=self.sr_number)
        return None

    class Meta:
        verbose_name = 'Domain Name'
