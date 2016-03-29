from clever_selects.admin import ChainedSelectAdminMixin
from django.contrib import admin

from .forms import RoomCreateForm
from .models import (Community, Building, Room, Department, SubDepartment, SiteAnnouncements,
                     StaffMapping, CSDMapping, TechFlair, UHInternalUser as InternalUser,
                     ADGroup, NavbarLink, PermissionClass)


class SiteAnnouncementsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created']


class StaffMappingAdmin(admin.ModelAdmin):
    list_display = ['title', 'name', 'email', 'extension']


class CSDMappingAdmin(admin.ModelAdmin):
    list_display = ['domain', 'name', 'email']


class TechFlairAdmin(admin.ModelAdmin):
    list_display = ['tech', 'flair']


class InternalUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'is_active']
    list_filter = ['is_active']


class BuildingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'community']


class RoomAdmin(ChainedSelectAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'building']
    list_filter = ['building']
    form = RoomCreateForm


class PermissionClassAdmin(admin.ModelAdmin):
    list_display = ['name']


class ADGroupAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'distinguished_name']


class NavBarLinkAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'sequence_index', 'parent_group']

admin.site.register(Community)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Department)
admin.site.register(SubDepartment)
admin.site.register(SiteAnnouncements, SiteAnnouncementsAdmin)
admin.site.register(StaffMapping, StaffMappingAdmin)
admin.site.register(CSDMapping, CSDMappingAdmin)
admin.site.register(TechFlair, TechFlairAdmin)
admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(PermissionClass, PermissionClassAdmin)
admin.site.register(ADGroup, ADGroupAdmin)
admin.site.register(NavbarLink, NavBarLinkAdmin)
