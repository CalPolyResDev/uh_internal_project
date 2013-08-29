from django.contrib import admin

from .models import CSDMapping, StaffMapping


class CSDMappingAdmin(admin.ModelAdmin):
    list_display = ('csd_domain', 'csd_alias', 'csd_name')


class StaffMappingAdmin(admin.ModelAdmin):
    list_display = ('staff_title', 'staff_alias', 'staff_name')

admin.site.register(CSDMapping, CSDMappingAdmin)
admin.site.register(StaffMapping, StaffMappingAdmin)
