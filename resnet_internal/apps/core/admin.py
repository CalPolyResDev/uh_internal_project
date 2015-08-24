from django.contrib import admin
from django.db import connection, transaction

from .models import Community, Building, Department, SubDepartment, SiteAnnouncements, StaffMapping, TechFlair, ResNetInternalUser, NetworkDevice


class SiteAnnouncementsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')


class StaffMappingAdmin(admin.ModelAdmin):
    list_display = ('staff_title', 'staff_alias', 'staff_name')


class TechFlairAdmin(admin.ModelAdmin):
    list_display = ('tech', 'flair')


class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'dns_name', 'ip_address')


class ResNetInternalUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_active',
                    'is_net_admin', 'is_telecom', 'is_tag', 'is_rn_staff', 'is_technician',
                    'is_new_tech', 'orientation_complete', 'is_developer')
    list_filter = ('is_active', 'is_net_admin', 'is_telecom', 'is_tag', 'is_rn_staff',
                   'is_technician', 'is_new_tech', 'is_developer')


admin.site.register(Community, admin.ModelAdmin)
admin.site.register(Building, admin.ModelAdmin)
admin.site.register(Department, admin.ModelAdmin)
admin.site.register(SubDepartment, admin.ModelAdmin)
admin.site.register(SiteAnnouncements, SiteAnnouncementsAdmin)
admin.site.register(StaffMapping, StaffMappingAdmin)
admin.site.register(TechFlair, TechFlairAdmin)
admin.site.register(ResNetInternalUser, ResNetInternalUserAdmin)
admin.site.register(NetworkDevice, NetworkDeviceAdmin)


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
