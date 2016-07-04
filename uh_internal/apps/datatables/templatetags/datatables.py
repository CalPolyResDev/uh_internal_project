"""
.. module:: resnet_internal.apps.datatables.templatetags
   :synopsis: University Housing Internal Datatables Template Tags and Filters.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>
"""

import logging

from django.core.exceptions import ImproperlyConfigured
from django.template import Library, TemplateSyntaxError

from ..ajax import RNINDatatablesPopulateView


logger = logging.getLogger(__name__)
register = Library()


@register.inclusion_tag('datatables/datatables_code.djhtml', takes_context=True)
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

        datatables_class_instance = datatables_class(request=context['request'])

        context.update(datatables_class_instance.get_context_data())
    else:
        raise ImproperlyConfigured("The datatables template tag requires the datatables class passed into context to not be None. (context['datatables_class'])")

    return context
