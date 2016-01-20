"""
.. module:: resnet_internal.apps.datatables.templatetags
   :synopsis: University Housing Internal Datatables Template Tags and Filters.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
"""

import logging

from django.core.exceptions import ImproperlyConfigured
from django.template import Library, TemplateSyntaxError
from django.core.urlresolvers import reverse_lazy


from ..ajax import RNINDatatablesPopulateView


logger = logging.getLogger(__name__)
register = Library()


@register.inclusion_tag('datatables/datatables_code.html', takes_context=True)
def datatables_script(context):
    """Renders Datatables Code into a django template."""

    try:
        datatables_class = context["datatables_class"]
    except KeyError:
        raise TemplateSyntaxError("The datatables template tag requires a datatables class to be passed into context. (context['datatables_class'])")

    # Add context
    if datatables_class:
        if not issubclass(datatables_class, RNINDatatablesPopulateView):
            raise ImproperlyConfigured("The populate_class instance variable is either not set or is not a subclass of RNINDatatablesPopulateView.")

        datatables_class_instance = datatables_class()
        datatables_class_instance._initialize_write_permissions(context["user"])

        context['datatable_name'] = datatables_class_instance.get_table_name()
        context['datatable_options'] = datatables_class_instance.get_options_serialized()
        context['datatable_update_url'] = datatables_class_instance.get_update_source()
        context['datatable_form_url'] = datatables_class_instance.get_form_source()
        context['write_permission'] = datatables_class_instance.get_write_permissions()
        context['remove_url'] = datatables_class_instance.get_remove_url()
        context['item_name'] = datatables_class_instance.get_item_name()
    else:
        raise ImproperlyConfigured("The datatables template tag requires the datatables class passed into context to not be None. (context['datatables_class'])")

    return context
