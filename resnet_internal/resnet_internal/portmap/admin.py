from django.contrib import admin

from .models import ResHallWired


class ResHallWiredAdmin(admin.ModelAdmin):
    list_display = ('community', 'building', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan')

admin.site.register(ResHallWired, ResHallWiredAdmin)
