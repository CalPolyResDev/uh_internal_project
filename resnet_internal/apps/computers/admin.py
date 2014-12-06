from django.contrib import admin

from .models import Computer


class ComputerAdmin(admin.ModelAdmin):
    list_display = ('department', 'sub_department', 'computer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description')

admin.site.register(Computer, ComputerAdmin)
