"""
.. module:: resnet_internal.datatables.ajax
   :synopsis: ResNet Internal Datatable Ajax Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import json
import logging
from collections import OrderedDict
from copy import deepcopy

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.forms import models as model_forms
from django.http.response import HttpResponseNotAllowed
from django.utils.encoding import smart_str
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from django_datatables_view.base_datatable_view import BaseDatatableView
from django_ajax.mixin import AJAXMixin

from resnet_internal.core.utils import dict_merge

logger = logging.getLogger(__name__)


class RNINDatatablesPopulateView(BaseDatatableView):
    """ The base datatable population view for ResNet Internal datatables."""

    table_name = "datatable"
    data_source = None
    update_source = None
    max_display_length = 200

    column_definitions = OrderedDict()
    options = {
        "order": [[1, "asc"], [2, "asc"], [3, "asc"]],
        "language": {
            "lengthMenu": 'Display <select>' +
                '<option value="25">25</option>' +
                '<option value="50">50</option>' +
                '<option value="100">100</option>' +
                '<option value="150">150</option>' +
                '<option value="200">200</option>' +
                '<option value="-1">All</option>' +
                '</select> records:',
            "search": "Filter records: ",
            "zeroRecords": "No records to display."
        },
        "processing": True,
        "serverSide": True,
        "pageLength": 50,
        "pagingType": "full_numbers",
        "lengthChange": True,
        "autoWidth": False,
        "dom": '<lrf><"clear">t<ip><"clear">',
    }

    extra_options = {}

    base_column_template = """
        <div id='{id}' class='{class_name}' column='{column}'>
        <div class='display_data'>
            {value}
            {link_block}
            {inline_images}
        </div>
        {editable_block}
        </div>
    """

    editable_block_template = """<input type='text' class='editbox' value='{value}' />"""
    link_block_template = """<a href='{link_url}' onclick='{onclick_action}' target='{link_target}' class='{link_class_name}' style='{link_style}'>{link_text}</a>"""
    icon_template = """<img src='{icon_url}' style='padding-left:5px;' align='top' width='16' height='16' border='0' />"""

    def initialize(self, *args, **kwargs):
        super(RNINDatatablesPopulateView, self).initialize(*args, **kwargs)

        if self.request:
            self._initialize_write_permissions(self.request.user)

    def get_table_name(self):
        return self.table_name

    def get_update_source(self):
        return self.update_source

    def _initialize_write_permissions(self, user):
        self.write_permissions = True

    def get_write_permissions(self):
        if not self.write_permissions:
            raise ImproperlyConfigured("Write permissions were not initialized.")

        return self.write_permissions

    def get_options(self):
        self.options.update({"ajax": str(self.data_source)})

        merged = dict_merge(self.options, self.extra_options)

        column_defs = deepcopy(self.column_definitions)
        formatted_column_defs = []

        for column_index, column_key in enumerate(column_defs):
            column_def = column_defs[column_key]
            column_def.update({"targets": [column_index]})
            formatted_column_defs.append(column_def)

        merged.update({"columnDefs": formatted_column_defs})
        return merged

    def get_options_serialized(self):
        return json.dumps(self.get_options())

    def get_columns(self):
        return self.column_definitions.keys()

    def _get_columns_by_attribute(self, attribute, default=True, test=True):
        """ Returns a filtered list of columns that have the given attribute.

        :param attribute: The attribute by which to filter
        :type attribute: str
        :param default: The default attribute value
        :param test: If the attribute is equal to this, return it

        """

        columns = []

        for column in self.column_definitions:
            if self.column_definitions[column].get(attribute, default) == test:
                columns.append(column)

        return columns

    def get_order_columns(self):
        return self.get_columns()

    def get_searchable_columns(self):
        return self._get_columns_by_attribute("searchable")

    def get_editable_columns(self):
        return self._get_columns_by_attribute("editable")

    def get_ip_address_columns(self):
        return self._get_columns_by_attribute("type", "", "ip-address")

    def render_column(self, row, column):
        """Renders columns with customized HTML.

        :param row: A dictionary containing row data.
        :type row: dict
        :param column: The name of the column to be rendered. This can be used to index into the row dictionary.
        :type column: str
        :returns: The HTML to be displayed for this column.

        """

        value = smart_str(getattr(row, column))

        if column in self.get_editable_columns() and self.get_write_permissions():
            editable_block = self.editable_block_template.format(value=value)
            return self.base_column_template.format(id=row.id, class_name="editable", column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
        else:
            return self.base_column_template.format(id=row.id, class_name="", column=column, value=value, link_block="", inline_images="", editable_block="")

    def filter_queryset(self, qs):
        """ Filters the QuerySet by submitted search parameters.

        Made to work with multiple word search queries.
        PHP source: http://datatables.net/forums/discussion/3343/server-side-processing-and-regex-search-filter/p1
        Credit for finding the Q.AND method: http://bradmontgomery.blogspot.com/2009/06/adding-q-objects-in-django.html

        :param qs: The QuerySet to be filtered.
        :type qs: QuerySet
        :returns: If search parameters exist, the filtered QuerySet, otherwise the original QuerySet.

        """

        search_parameters = self.request.GET.get('search[value]', None)
        searchable_columns = self.get_searchable_columns()

        if search_parameters:
            params = search_parameters.split(" ")
            columnQ = Q()
            paramQ = Q()

            for param in params:
                if param != "":
                    for searchable_column in searchable_columns:
                        columnQ |= Q(**{searchable_column + "__icontains": param})

                    paramQ.add(columnQ, Q.AND)
                    columnQ = Q()
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class BaseDatatablesUpdateView(AJAXMixin, ModelFormMixin, ProcessFormView):
    """ Base class to update datatable rows."""

    model = None
    object = None
    form_class = None
    populate_class = None

    def dispatch(self, request, *args, **kwargs):
        if not self.populate_class or not issubclass(self.populate_class, RNINDatatablesPopulateView):
            raise ImproperlyConfigured("The populate_class instance variable is either not set or is not a subclass of RNINDatatablesPopulateView.")
        else:
            self.populate_class_instance = self.populate_class()
            self.populate_class_instance._initialize_write_permissions(request.user)

        self.fields = self.form_class._meta.fields

        return super(BaseDatatablesUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed

    def get_form_class(self):
        return model_forms.modelform_factory(self.model, form=self.form_class, fields=self.fields)

    def post(self, request, *args, **kwargs):
        instance_id = request.POST.get("id", None)

        if instance_id:
            self.object = self.model.objects.get(id=instance_id)

        return super(BaseDatatablesUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        rendered_columns = {}

        for field in self.fields:
            rendered_columns[field] = self.populate_class_instance.render_column(self.object, field)

        context = {}
        context["form_valid"] = True
        context["rendered_columns"] = rendered_columns

        return context

    def form_invalid(self, form):
        form_errors = form.non_field_errors()
        field_errors = [field.errors for field in form if field.errors]

        context = {}
        context["form_valid"] = False
        context["form_errors"] = form_errors
        context["field_errors"] = field_errors

        return context


def redraw_row(request, populate_class, row_id):
    if not issubclass(populate_class, RNINDatatablesPopulateView):
        raise ImproperlyConfigured("The populate_class instance variable is either not set or is not a subclass of RNINDatatablesPopulateView.")

    populate_class_instance = populate_class()
    populate_class_instance._initialize_write_permissions(request.user)

    fields = populate_class_instance.get_columns()
    queryset = populate_class_instance.model.objects.get(id=row_id)

    rendered_columns = {}

    for field in fields:
        rendered_columns[field] = populate_class_instance.render_column(queryset, field)

    return {"rendered_columns": rendered_columns}