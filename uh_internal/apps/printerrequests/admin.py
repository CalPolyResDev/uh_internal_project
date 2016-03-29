from django.contrib import admin

from .models import PrinterType, Toner, Part, Request, InventoryEmail


admin.site.register(PrinterType)
admin.site.register(Toner)
admin.site.register(Part)
admin.site.register(Request)
admin.site.register(InventoryEmail)
