from clever_selects.admin import ChainedSelectAdminMixin
from django.contrib import admin

from .forms import AccessPointCreateForm, PortCreateForm
from .models import Port, AccessPoint, NetworkDevice, NetworkInfrastructureDevice


class PortAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'active']
    form = PortCreateForm

admin.site.register(Port, PortAdmin)


class AccessPointAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['display_name', 'mac_address', 'ip_address', 'port', 'ap_type']
    form = AccessPointCreateForm


admin.site.register(AccessPoint, AccessPointAdmin)


class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'mac_address', 'ip_address', 'dns_name', 'upstream_device']

admin.site.register(NetworkDevice, NetworkDeviceAdmin)


class NetworkInfrastructureDeviceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'dns_name', 'ip_address']

admin.site.register(NetworkInfrastructureDevice, NetworkInfrastructureDeviceAdmin)
