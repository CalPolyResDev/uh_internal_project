from django.contrib import admin

from .models import Printer


class PrinterAdmin(admin.ModelAdmin):
    list_display = ['department', 'sub_department', 'display_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'location', 'date_purchased', 'description']
    list_filter = ['dhcp']

admin.site.register(Printer, PrinterAdmin)
