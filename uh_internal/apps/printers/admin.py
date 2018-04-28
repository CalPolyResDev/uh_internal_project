"""
.. module:: resnet_internal.apps.printers.admin
   :synopsis: University Housing Internal Printer Index admin registration.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.contrib import admin

from .models import Printer


class PrinterAdmin(admin.ModelAdmin):
    """ Sets the display attributes for the printers admin panel """

    list_display = ['department',
                    'sub_department',
                    'display_name',
                    'ip_address',
                    'mac_address',
                    'model',
                    'serial_number',
                    'property_id',
                    'location',
                    'date_purchased',
                    'description']
    list_filter = ['dhcp']

admin.site.register(Printer, PrinterAdmin)
