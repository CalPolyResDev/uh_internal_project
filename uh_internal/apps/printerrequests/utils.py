"""
.. module:: resnet_internal.apps.printerrequests.utils
   :synopsis: University Housing Internal Printer Request Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import datetime

from django.core.mail import send_mail

from ..core.models import StaffMapping
from .models import Request, Toner, Part, InventoryEmail


INVENTORY_LOW_CUTOFF = 5
LAST_EMAIL_DELTA = datetime.timedelta(days=1)


def can_fulfill_request(request_id):
    """Determines if there are enough items in inventory to complete a request."""

    printer_request = Request.objects.get(id=request_id)
    toner_quantity_map = {}
    part_quantity_map = {}

    can_fulfill_request = True

    # Add cartridge quantities
    for cartridge in printer_request.toner.all():
        toner_quantity_map[cartridge.id] = cartridge.quantity

    # Add part quantities
    for part in printer_request.parts.all():
        part_quantity_map[part.id] = part.quantity

    # Decrement each cartridge quantity
    for cartridge in printer_request.toner.all():
        toner_quantity_map[cartridge.id] = toner_quantity_map[cartridge.id] - 1

        # Check if there's enough inventory to fulfill the request
        if toner_quantity_map[cartridge.id] < 0:
            can_fulfill_request = False

    # Decrement each part quantity
    for part in printer_request.parts.all():
        part_quantity_map[part.id] = part_quantity_map[part.id] - 1

        # Check if there's enough inventory to fulfill the request
        if part_quantity_map[part.id] < 0:
            can_fulfill_request = False

    return can_fulfill_request


def send_replenishment_email():
    """Sends an email to the assistant resident coordinator if inventory is low."""

    assistant_coord_email = StaffMapping.objects.get(title="ResNet: Assistant Resident Coordinator").email

    low_toner_cartridges = Toner.objects.extra(where=["quantity + ordered < %d" % INVENTORY_LOW_CUTOFF])
    low_parts = Part.objects.extra(where=["quantity + ordered < %d" % INVENTORY_LOW_CUTOFF])

    low_inventory_exists = low_toner_cartridges.exists() or low_parts.exists()

    try:
        latest_email = InventoryEmail.objects.latest(field_name="date_sent")
        email_sent_today = latest_email.date_sent > datetime.datetime.now() - LAST_EMAIL_DELTA
    except InventoryEmail.DoesNotExist:
        email_sent_today = False

    if low_inventory_exists and not email_sent_today:
        message = """This email is a reminder that some inventory items are below %s in quantity.\n\n\n""" % str(INVENTORY_LOW_CUTOFF)

        # Send the low toner alert
        if low_toner_cartridges.exists():
            message += """Inventory of the following toner cartridges is low:\n"""

            for cartridge in low_toner_cartridges:
                message += """\t%s\n""" % cartridge

        # Send the low parts alert
        if low_parts.exists():
            message += """\n\nInventory of the following printer parts is low:\n"""

            for part in low_parts:
                message += """\t%s\n""" % part

        email = InventoryEmail(email=message)
        email.save()

        send_mail(subject='[University Housing Internal] Low Inventory Notification', message=message, from_email=None, recipient_list=[assistant_coord_email])


def send_delivery_confirmation(request):
    message = "Hi,\n\nYour request for the following printer items has been fulfilled:\n"

    for cartridge in request.toner.all():
        message += """\t%s\n""" % cartridge

    for part in request.parts.all():
        message += """\t%s\n""" % part

    message += "\nHave a wonderful day!\n\nRegards,\nResNet Staff"

    send_mail(subject='[ResLife Internal] Printer Request Notification', message=message, from_email=None, recipient_list=[request.requestor + "@calpoly.edu"])
