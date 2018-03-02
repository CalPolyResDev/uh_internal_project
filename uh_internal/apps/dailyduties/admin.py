from django.contrib import admin

from .models import DailyDuties


class DailyDutiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_checked', 'last_user')


admin.site.register(DailyDuties, DailyDutiesAdmin)
