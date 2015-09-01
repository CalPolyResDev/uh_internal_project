from django.contrib import admin
from django.db import connection, transaction

from .models import DailyDuties


class DailyDutiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_checked', 'last_user')


admin.site.register(DailyDuties, admin.ModelAdmin)
