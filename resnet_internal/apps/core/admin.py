from django.contrib import admin
from django.db import connection, transaction

from resnet_internal.apps.core.models import NavbarLink

from .models import Community, Building, Room, Department, SubDepartment, SiteAnnouncements, StaffMapping, TechFlair, ResNetInternalUser, NetworkDevice, ADGroup


class SiteAnnouncementsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created']


class StaffMappingAdmin(admin.ModelAdmin):
    list_display = ['staff_title', 'staff_alias', 'staff_name']


class TechFlairAdmin(admin.ModelAdmin):
    list_display = ['tech', 'flair']


class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'dns_name', 'ip_address']


class ResNetInternalUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'is_active',
                    'is_net_admin', 'is_telecom', 'is_tag', 'is_rn_staff', 'is_technician',
                    'is_new_tech', 'orientation_complete', 'is_developer']
    list_filter = ['is_active', 'is_net_admin', 'is_telecom', 'is_tag', 'is_rn_staff',
                   'is_technician', 'is_new_tech', 'is_developer']


class BuildingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'community']


class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'building']
    list_filter = ['building']


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
admin.site.register(TechFlair, TechFlairAdmin)
admin.site.register(ResNetInternalUser, ResNetInternalUserAdmin)
admin.site.register(NetworkDevice, NetworkDeviceAdmin)
admin.site.register(ADGroup, ADGroupAdmin)
admin.site.register(NavbarLink, NavBarLinkAdmin)


def sync_rms_data():
    cursor = connection.cursor()

    # Purge Building and Community Data
    Building.objects.all().delete()
    Community.objects.all().delete()

    # Copy data from master to slave
    cursor.execute("INSERT INTO resnet_internal.core_building SELECT * FROM common.core_building")
    cursor.execute("INSERT INTO resnet_internal.core_community SELECT * FROM common.core_community")
    cursor.execute("INSERT INTO resnet_internal.core_community_buildings SELECT * FROM common.core_community_buildings")

    transaction.commit()
