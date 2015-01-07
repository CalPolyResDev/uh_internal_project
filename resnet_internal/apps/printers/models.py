"""
.. module:: resnet_internal.apps.printers.models
   :synopsis: ResNet Internal Printer Index Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models.base import Model
from django.db.models.fields import CharField, GenericIPAddressField

from ..computers.fields import MACAddressField
from ..computers.constants import DEPARTMENTS, ALL_SUB_DEPARTMENTS


class Printer(Model):
    """University Housing printers."""

    DEPARTMENT_CHOICES = [(department, department) for department in DEPARTMENTS]
    SUB_DEPARTMENT_CHOICES = [(sub_department, sub_department) for sub_department in ALL_SUB_DEPARTMENTS]

    department = CharField(max_length=50, verbose_name='Department', choices=DEPARTMENT_CHOICES)
    sub_department = CharField(max_length=50, verbose_name='Sub Department', choices=SUB_DEPARTMENT_CHOICES)
    printer_name = CharField(max_length=60, verbose_name='Printer Name', unique=True)
    ip_address = GenericIPAddressField(protocol='IPv4', verbose_name='IP Address', unique=True)
    mac_address = MACAddressField(verbose_name='MAC Address', unique=True)
    model = CharField(max_length=25, verbose_name='Model')
    serial_number = CharField(max_length=20, verbose_name='Serial Number', unique=True)
    property_id = CharField(max_length=50, verbose_name='Cal Poly Property ID', unique=True)
    description = CharField(max_length=100, verbose_name='Description')

    def __str__(self):
        return self.printer_name

    def save(self, *args, **kwargs):
        for field_name in ['printer_name', 'mac_address', 'serial_number', 'property_id']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())
        super(Printer, self).save(*args, **kwargs)

    class Meta:
        db_table = 'printer'
        managed = False
        verbose_name = 'University Housing Printer'
