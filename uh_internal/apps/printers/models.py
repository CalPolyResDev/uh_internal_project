"""
.. module:: resnet_internal.apps.printers.models
   :synopsis: University Housing Internal Printer Index Models.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.db.models.deletion import CASCADE
from django.db.models.fields import BooleanField, CharField, DateField
from django.db.models.fields.related import ForeignKey

from ..core.models import Department, SubDepartment
from ..network.models import NetworkDevice


class Printer(NetworkDevice):
    """ The model for printer data storage """

    department = ForeignKey(Department, verbose_name='Department', on_delete=CASCADE)
    sub_department = ForeignKey(SubDepartment, verbose_name='Sub Department', on_delete=CASCADE)

    model = CharField(max_length=25, verbose_name='Model')
    serial_number = CharField(max_length=20, verbose_name='Serial Number', blank=True,
                              null=True, unique=True, default=None)
    property_id = CharField(max_length=50, verbose_name='Cal Poly Property ID', blank=True,
                            null=True, unique=True, default=None)

    location = CharField(max_length=100, verbose_name='Location', blank=True, null=True)
    date_purchased = DateField(verbose_name='Date Purchased')
    description = CharField(max_length=100, verbose_name='Description')

    dhcp = BooleanField(default=False)

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        """Uppercase field names on save."""

        for field_name in ['printer_name', 'mac_address', 'serial_number', 'property_id']:
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

        if self.dhcp:
            self.ip_address = None

        super(Printer, self).save(*args, **kwargs)
