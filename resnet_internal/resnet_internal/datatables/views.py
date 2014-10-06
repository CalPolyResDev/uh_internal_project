"""
.. module:: resnet_internal.datatables.views
   :synopsis: ResNet Internal Residence Halls Datatable Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from django.core.exceptions import ImproperlyConfigured
from django.views.generic.edit import CreateView

from resnet_internal.datatables.ajax import RNINDatatablesPopulateView


class DatatablesView(CreateView):
    populate_class = None

    def __init__(self, **kwargs):
        super(DatatablesView, self).__init__(**kwargs)

        if not issubclass(self.populate_class, RNINDatatablesPopulateView):
            raise ImproperlyConfigured("The populate_class instance variable is either not set or is not a subclass of RNINDatatablesPopulateView.")

    def get_context_data(self, **kwargs):
        context = super(DatatablesView, self).get_context_data(**kwargs)
        context["datatables_class"] = self.populate_class
        return context
