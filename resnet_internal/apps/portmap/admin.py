from django.contrib import admin

from clever_selects.admin import ChainedSelectAdminMixin

from .forms import AccessPointCreateForm, ResHallWiredPortCreateForm
from .models import ResHallWired, AccessPoint


class ResHallWiredAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ('room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan', 'active',)
    form = ResHallWiredPortCreateForm

admin.site.register(ResHallWired, ResHallWiredAdmin)


class AccessPointAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'mac_address', 'ip_address', 'port')
    form = AccessPointCreateForm

admin.site.register(AccessPoint, AccessPointAdmin)
