"""
.. module:: resnet_internal.apps.dailyduties.admin
   :synopsis: University Housing Internal Daily Duties admin registration.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.contrib import admin

from .models import DailyDuties


class DailyDutiesAdmin(admin.ModelAdmin):
    """ Sets the display attributes for the daily duties admin panel """

    list_display = ('name', 'last_checked', 'last_user')


admin.site.register(DailyDuties, DailyDutiesAdmin)
