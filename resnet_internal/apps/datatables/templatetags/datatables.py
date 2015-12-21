"""
.. module:: resnet_internal.apps.datatables.templatetags
   :synopsis: University Housing Internal Datatables Template Tags and Filters.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
"""

import logging

from django.core.exceptions import ImproperlyConfigured
from django.template import Context, loader, Library, Node, TemplateSyntaxError

from ..ajax import RNINDatatablesPopulateView


logger = logging.getLogger(__name__)
register = Library()


@register.tag(name="datatables_script")
def do_datatables(parser, token):
    return DatatablesNode()


class DatatablesNode(Node):
    """Renders Datatables Code into a django template. Designed to be thread safe."""

    template_name = 'datatables/datatables_code.html'

    def render(self, context):
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
            context['write_permission'] = datatables_class_instance.get_write_permissions()

            template = loader.get_template(self.template_name)

            return template.render(Context(context))
        else:
            return ''
