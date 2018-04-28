from django.contrib import admin

from .models import Uploaders


class UploadersAdmin(admin.ModelAdmin):
    list_display = ['name', 'last_run', 'successful']
    list_filter = ['last_run']

admin.site.register(Uploaders, UploadersAdmin)
