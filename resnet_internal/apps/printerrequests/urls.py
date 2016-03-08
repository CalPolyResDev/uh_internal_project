"""
.. module:: resnet_internal.apps.printerrequests.urls
   :synopsis: University Housing Internal Printer Requests URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import daily_duties_access
from .ajax import change_request_status, update_part_inventory, update_toner_inventory
from .views import RequestsListView, InventoryView, OnOrderView

app_name = 'printerrequests'

urlpatterns = [
    url(r'^list/', login_required(daily_duties_access(RequestsListView.as_view())), name='list'),
    url(r'^view_inventory/', login_required(daily_duties_access(InventoryView.as_view())), name='inventory'),
    url(r'^view_ordered/', login_required(daily_duties_access(OnOrderView.as_view())), name='ordered_items'),
    url(r'^change_status/', login_required(daily_duties_access(change_request_status)), name='change_status'),
    url(r'^toner/update_inventory/', login_required(daily_duties_access(update_toner_inventory)), name='update_toner_inventory'),
    url(r'^parts/update_inventory/', login_required(daily_duties_access(update_part_inventory)), name='update_part_inventory'),
]