from django.db.models.base import Model
from django.db.models.fields import CharField, GenericIPAddressField
from django.db.models.fields.related import OneToOneField

from resnet_internal.apps.computers.fields import MACAddressField
from resnet_internal.apps.portmap.models import ResHallWired


class AccessPoint(Model):
    TYPE_CHOICES = (
        ('5', '5 Ghz'),
        ('2.4', '2.4 Ghz'),
        ('AM', 'Air Monitor'),
    )

    name = CharField(max_length=30, verbose_name='DNS Name')
    property_id = CharField(max_length=7, unique=True, verbose_name='Property ID')
    serial_number = CharField(max_length=9, unique=True, verbose_name='Serial Number')
    mac_address = MACAddressField(unique=True, verbose_name='MAC Address')
    port = OneToOneField(ResHallWired, related_name='access_point')
    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address')
    type = CharField(max_length=3, choices=TYPE_CHOICES, verbose_name='Type')
