from django.contrib import admin

from .models import Printer, PrinterType, Toner, Part, Request, Request_Toner, Request_Parts, InventoryEmail


class PrinterAdmin(admin.ModelAdmin):
    list_display = ('department', 'sub_department', 'printer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description')

admin.site.register(Printer, PrinterAdmin)
admin.site.register(PrinterType)
admin.site.register(Toner)
admin.site.register(Part)
admin.site.register(Request)
admin.site.register(Request_Toner)
admin.site.register(Request_Parts)
admin.site.register(InventoryEmail)
