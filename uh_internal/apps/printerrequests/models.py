"""
.. module:: resnet_internal.apps.printerrequests.models
   :synopsis: University Housing Internal Printer Request Models.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.db.models.base import Model
from django.db.models.fields import (CharField, TextField, PositiveIntegerField,
                                     IntegerField, DateTimeField, BooleanField)
from django.db.models.fields.related import ForeignKey, ManyToManyField


class PrinterType(Model):
    """A printer used in University Housing."""

    make = CharField(max_length=10)
    model = CharField(max_length=10)
    servicable = BooleanField(default=False)

    def __str__(self):
        return self.make + " " + self.model

    class Meta:
        unique_together = ['make', 'model']
        verbose_name = 'Printer Type'


class Toner(Model):
    """A toner cartrige for a particular printer."""

    color = CharField(max_length=10)
    printer = ForeignKey(PrinterType, verbose_name='Associated Printer')
    quantity = PositiveIntegerField(default=0)
    ordered = PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.color)

    class Meta:
        unique_together = ['color', 'printer']
        verbose_name = 'Printer Toner Cartridge'


class Part(Model):
    """A part for a particular printer."""

    type = CharField(max_length=25, verbose_name='Type of Part')
    printer = ForeignKey(PrinterType, verbose_name='Associated Printer')
    quantity = PositiveIntegerField(default=0)
    ordered = PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.type)

    class Meta:
        unique_together = ['type', 'printer']
        verbose_name = 'Printer Part'


REQUEST_STATUSES = ['Open', 'Acknowledged', 'In Transit', 'Delivered']


class Request(Model):
    """A request for toner and/or parts replacement."""

    STATUSES = REQUEST_STATUSES
    REQUEST_STATUS_CHOICES = [(REQUEST_STATUSES.index(status), status) for status in REQUEST_STATUSES]

    ticket_id = IntegerField(unique=True)
    date_requested = DateTimeField()
    priority = CharField(max_length=25)
    requestor = CharField(max_length=50)
    toner = ManyToManyField(Toner, blank=True)
    parts = ManyToManyField(Part, blank=True)
    address = CharField(max_length=50)
    status = IntegerField(choices=REQUEST_STATUS_CHOICES, blank=False)

    def __str__(self):
        return str(self.ticket_id) + " - " + self.STATUSES[self.status].upper()

    class Meta:
        verbose_name = 'Printer Request'


class InventoryEmail(Model):
    """Keeps track of inventory replenishment emails."""

    email = TextField(blank=False)
    date_sent = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Printer Inventory Email'
