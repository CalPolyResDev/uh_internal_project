from django.contrib import admin

from .forms import AccessPointCreateForm
from .models import ResHallWired, AccessPoint


class ResHallWiredAdmin(admin.ModelAdmin):
    list_display = ('community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan', 'active',)

admin.site.register(ResHallWired, ResHallWiredAdmin)


class AccessPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'mac_address', 'ip_address', 'port')
    form = AccessPointCreateForm

admin.site.register(AccessPoint, AccessPointAdmin)
