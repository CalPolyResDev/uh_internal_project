from django.contrib import admin

from .models import Computer, Pinhole


class ComputerAdmin(admin.ModelAdmin):
    list_display = ['department', 'sub_department', 'display_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'location', 'date_purchased', 'dn', 'description']
    list_filter = ['dhcp']


class PinholeAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'service_name', 'inner_fw', 'border_fw', 'tcp_ports', 'udp_ports']
    list_filter = ['service_name']

admin.site.register(Computer, ComputerAdmin)
admin.site.register(Pinhole, PinholeAdmin)
