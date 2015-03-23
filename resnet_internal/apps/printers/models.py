"""
.. module:: resnet_internal.apps.printers.models
   :synopsis: ResNet Internal Printer Index Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models.base import Model
from django.db.models.fields import CharField, GenericIPAddressField
from django.db.models.fields.related import ForeignKey

from ..core.models import Department, SubDepartment
from ..computers.fields import MACAddressField


class Printer(Model):
    """University Housing printers."""

    department = ForeignKey(Department, verbose_name='Department')
    sub_department = ForeignKey(SubDepartment, verbose_name='Sub Department')
    printer_name = CharField(max_length=60, verbose_name='Printer Name', unique=True)
    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address', unique=True)
    mac_address = MACAddressField(verbose_name='MAC Address', unique=True)
    model = CharField(max_length=25, verbose_name='Model')
    serial_number = CharField(max_length=20, verbose_name='Serial Number', blank=True, null=True, unique=True, default=None)
    property_id = CharField(max_length=50, verbose_name='Cal Poly Property ID', blank=True, null=True, unique=True, default=None)
    location = CharField(max_length=100, verbose_name='Location', blank=True, null=True)
    description = CharField(max_length=100, verbose_name='Description')

    def __str__(self):
        return self.printer_name

    def save(self, *args, **kwargs):
        """Uppercase field names on save."""

        for field_name in ['printer_name', 'mac_address', 'serial_number', 'property_id']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        for field_name in ['serial_number', 'property_id']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())
        super(Printer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'University Housing Printer'
