"""
.. module:: resnet_internal.apps.printerrequests.urls
   :synopsis: University Housing Internal Printer Requests URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import daily_duties_access, printer_request_create_access
from .ajax import change_request_status, update_part_inventory, update_toner_inventory, update_toner, update_part
from .views import RequestsListView, InventoryView, OnOrderView, RequestTonerView, RequestPartsView

app_name = 'printerrequests'

urlpatterns = [
    url(r'^$', login_required(printer_request_create_access(RequestsListView.as_view())), name='home'),
    url(r'^change_status/$', login_required(daily_duties_access(change_request_status)), name='change_status'),

    url(r'^toner/', login_required(printer_request_create_access(RequestTonerView.as_view())), name='toner_request'),
    url(r'^parts/', login_required(printer_request_create_access(RequestPartsView.as_view())), name='parts_request'),
    url(r'^ajax/update_toner/', login_required(printer_request_create_access(update_toner)), name='ajax_update_printer_toner_cartridge'),
    url(r'^ajax/update_part/', login_required(printer_request_create_access(update_part)), name='ajax_update_printer_part'),

    url(r'^view_inventory/$', login_required(daily_duties_access(InventoryView.as_view())), name='inventory'),
    url(r'^view_ordered/$', login_required(daily_duties_access(OnOrderView.as_view())), name='ordered_items'),
    url(r'^toner/update_inventory/$', login_required(daily_duties_access(update_toner_inventory)), name='update_toner_inventory'),
    url(r'^parts/update_inventory/$', login_required(daily_duties_access(update_part_inventory)), name='update_part_inventory'),
]
