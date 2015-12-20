from clever_selects.admin import ChainedSelectAdminMixin
from django.contrib import admin

from .forms import AccessPointCreateForm, PortCreateForm
from .models import Port, AccessPoint


class PortAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'active']
    form = PortCreateForm

admin.site.register(Port, PortAdmin)


class AccessPointAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'mac_address', 'ip_address', 'port', 'ap_type']
    form = AccessPointCreateForm

admin.site.register(AccessPoint, AccessPointAdmin)
