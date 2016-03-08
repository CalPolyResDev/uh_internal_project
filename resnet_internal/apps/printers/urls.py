"""
.. module:: resnet_internal.apps.printers.urls
   :synopsis: University Housing Internal Printers URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import printers_access, printers_modify_access
from .ajax import PopulatePrinters, UpdatePrinter, RetrievePrinterForm, RemovePrinter
from .views import PrintersView

app_name = 'printers'

urlpatterns = [
    url(r'^printers/$', login_required(printers_access(PrintersView.as_view())), name='printers'),
    url(r'^printers/populate/$', login_required(printers_access(PopulatePrinters.as_view())), name='populate_printers'),
    url(r'^printers/update/$', login_required(printers_modify_access(UpdatePrinter.as_view())), name='update_printer'),
    url(r'^printers/form/$', login_required(printers_access(RetrievePrinterForm.as_view())), name='form_printer'),
    url(r'^printers/remove/$', login_required(printers_modify_access(RemovePrinter.as_view())), name='remove_printer'),
]
