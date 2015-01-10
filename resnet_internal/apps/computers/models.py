"""
.. module:: resnet_internal.apps.computers.models
   :synopsis: ResNet Internal Computer Index Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models.base import Model
from django.db.models.fields import BooleanField, CharField, IntegerField, GenericIPAddressField
from django.db.models.fields.related import ForeignKey

from ..core.models import Department, SubDepartment
from .fields import MACAddressField, ListField


class Computer(Model):
    """University Housing computers."""

    department = ForeignKey(Department, verbose_name='Department')
    sub_department = ForeignKey(SubDepartment, verbose_name='Sub Department')
    computer_name = CharField(max_length=25, verbose_name='Computer Name', unique=True)
    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address', unique=True)
    mac_address = MACAddressField(verbose_name='MAC Address', unique=True)
    model = CharField(max_length=25, verbose_name='Model')
    serial_number = CharField(max_length=20, verbose_name='Serial Number', blank=True, null=True, unique=True, default=None)
    property_id = CharField(max_length=50, verbose_name='Cal Poly Property ID', blank=True, null=True, unique=True, default=None)
    dn = CharField(max_length=250, verbose_name='Distinguished Name')
    description = CharField(max_length=100, verbose_name='Description')

    def __str__(self):
        return self.computer_name

    def save(self, *args, **kwargs):
        """Uppercase field names on save."""

        for field_name in ['computer_name', 'mac_address', 'serial_number', 'property_id']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())
        super(Computer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'University Housing Computer'


class Pinhole(Model):
    """University Housing Firewall Pinholes."""

    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')
    service_name = CharField(max_length=50, verbose_name='Service Name')
    inner_fw = BooleanField(default=None, verbose_name='Inner Firewall')
    border_fw = BooleanField(default=None, verbose_name='Border Firewall')
    tcp_ports = ListField(verbose_name='TCP Ports')
    udp_ports = ListField(verbose_name='TCP Ports')
    sr_number = IntegerField(max_length=11, null=True, verbose_name='SR Number', db_column='ticket_id')

    def __str__(self):
        return 'Pinhole: ' + str(self.ip_address)

    class Meta:
        verbose_name = 'University Housing Pinhole'


class DomainName(Model):
    """University Housing Domain Names."""

    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')
    domain_name = CharField(max_length=100, verbose_name='Domain Name')
    sr_number = IntegerField(max_length=11, null=True, verbose_name='SR Number', db_column='ticket_id')

    def __str__(self):
        return 'DNS Record: ' + str(self.ip_address)

    class Meta:
        verbose_name = 'University Housing Domain Name'
