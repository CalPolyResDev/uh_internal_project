"""
.. module:: resnet_internal.apps.printerrequests.models
   :synopsis: ResNet Internal Printer Request Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models.base import Model
from django.db.models.fields import (CharField, TextField, PositiveIntegerField,
                                     IntegerField, DateTimeField)
from django.db.models.fields.related import ForeignKey, ManyToManyField


class PrinterType(Model):
    """A printer used in University Housing."""

    make = CharField(max_length=10, verbose_name='Make')
    model = CharField(max_length=10, verbose_name='Model')

    def __str__(self):
        return self.make + " " + self.model

    class Meta:
        unique_together = ('make', 'model',)
        db_table = 'printertype'
        managed = False
        verbose_name = 'Printer Type'


class Toner(Model):
    """A toner cartrige for a particular printer."""

    color = CharField(max_length=10, verbose_name='Color')
    printer = ForeignKey(PrinterType, verbose_name='Associated Printer')
    quantity = PositiveIntegerField(default=0, verbose_name='Quantity')
    ordered = PositiveIntegerField(default=0, verbose_name='Ordered')

    def __str__(self):
        return str(self.printer) + " " + str(self.color)

    class Meta:
        unique_together = ('color', 'printer',)
        db_table = 'toner'
        managed = False
        verbose_name = 'Printer Toner Cartridge'


class Part(Model):
    """A part for a particular printer."""

    type = CharField(max_length=25, verbose_name='Type of Part')
    printer = ForeignKey(PrinterType, verbose_name='Associated Printer')
    quantity = PositiveIntegerField(default=0, verbose_name='Quantity')
    ordered = PositiveIntegerField(default=0, verbose_name='Ordered')

    def __str__(self):
        return str(self.printer) + " " + str(self.type)

    class Meta:
        unique_together = ('type', 'printer',)
        db_table = 'part'
        managed = False
        verbose_name = 'Printer Part'


REQUEST_STATUSES = ['Open', 'Acknowledged', 'In Transit', 'Delivered']


class Request(Model):
    """A request for toner and/or parts replacement."""

    STATUSES = REQUEST_STATUSES
    STATUS_CHOICES = [(REQUEST_STATUSES.index(status), status) for status in REQUEST_STATUSES]

    ticket_id = IntegerField(unique=True)
    date_requested = DateTimeField()
    priority = CharField(max_length=25)
    requestor = CharField(max_length=14)
    toner = ManyToManyField(Toner, through='Request_Toner')
    parts = ManyToManyField(Part, through='Request_Parts')
    address = CharField(max_length=50)
    status = IntegerField(choices=STATUS_CHOICES, blank=False)

    def add_toner(self, toner_cartridges):
        """Adds toner cartriges to this request.

        :param toner_cartridges: An iterable of toner cartriges.
        :type toner_cartridges: iterable

        """

        for cartridge in toner_cartridges:
            toner_m2m = Request_Toner()
            toner_m2m.request = self
            toner_m2m.toner = cartridge
            toner_m2m.save()

    def add_parts(self, parts):
        """Adds parts to this request.

        :param parts: An iterable of parts.
        :type parts: iterable

        """

        for part in parts:
            parts_m2m = Request_Parts()
            parts_m2m.request = self
            parts_m2m.part = part
            parts_m2m.save()

    def __str__(self):
        return str(self.ticket_id) + " - " + self.STATUSES[self.status].upper()

    class Meta:
        db_table = 'request'
        managed = False
        verbose_name = 'Printer Request'


class Request_Toner(Model):
    """Join table for the toner many-to-many field in Request."""

    request = ForeignKey(Request)
    toner = ForeignKey(Toner)

    class Meta:
        db_table = 'request_toner'
        managed = False
        verbose_name = 'Printer Request Toner'
        verbose_name_plural = 'Printer Request Toner Items'


class Request_Parts(Model):
    """Join table for the parts many-to-many field in Request."""

    request = ForeignKey(Request)
    part = ForeignKey(Part)

    class Meta:
        db_table = 'request_parts'
        managed = False
        verbose_name = 'Printer Request Parts'
        verbose_name_plural = 'Printer Request Parts Items'


class InventoryEmail(Model):
    """Keeps track of inventory replenishment emails."""

    email = TextField(blank=False)
    date_sent = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Printer Inventory Email'
