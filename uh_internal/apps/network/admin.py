from clever_selects.admin import ChainedSelectAdminMixin
from django.contrib import admin

from .forms import AccessPointCreateForm, PortCreateForm
from .models import Port, AccessPoint, NetworkDevice, NetworkInfrastructureDevice, ClearPassLoginAttempt


class PortAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['room', 'upstream_device', 'display_name', 'blade_number', 'port_number', 'active']
    form = PortCreateForm

admin.site.register(Port, PortAdmin)


class AccessPointAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['display_name', 'mac_address', 'ip_address', 'upstream_device', 'ap_type', 'airwaves_id']
    form = AccessPointCreateForm


admin.site.register(AccessPoint, AccessPointAdmin)


class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'mac_address', 'ip_address', 'dns_name', 'upstream_device']

admin.site.register(NetworkDevice, NetworkDeviceAdmin)


class NetworkInfrastructureDeviceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'dns_name', 'ip_address']

admin.site.register(NetworkInfrastructureDevice, NetworkInfrastructureDeviceAdmin)


class ClearPassLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'time', 'client_mac_address', 'service', 'result', 'roles', 'enforcement_profiles']

admin.site.register(ClearPassLoginAttempt, ClearPassLoginAttemptAdmin)
