from django.contrib import admin

from .models import DailyDuties, EmailPermalink


class DailyDutiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_checked', 'last_user')


class EmailPermalinkAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'sender_email', 'subject', 'slug')


admin.site.register(DailyDuties, DailyDutiesAdmin)
admin.site.register(EmailPermalink, EmailPermalinkAdmin)