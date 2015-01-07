from django.contrib import admin

from .models import Printer


class PrinterAdmin(admin.ModelAdmin):
    list_display = ('department', 'sub_department', 'printer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'description')

admin.site.register(Printer, PrinterAdmin)
