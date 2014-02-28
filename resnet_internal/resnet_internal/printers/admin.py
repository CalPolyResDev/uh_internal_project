from django.contrib import admin

from .models import PrinterType, Toner, Part, Request, Request_Toner, Request_Parts, InventoryEmail

admin.site.register(PrinterType)
admin.site.register(Toner)
admin.site.register(Part)
admin.site.register(Request)
admin.site.register(Request_Toner)
admin.site.register(Request_Parts)
admin.site.register(InventoryEmail)
