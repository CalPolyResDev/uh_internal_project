"""
.. module:: resnet_internal.apps.datatables.ajax
   :synopsis: ResNet Internal Datatable Ajax Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict
from copy import deepcopy
import json
import logging
import shlex

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.forms import models as model_forms
from django.http.response import HttpResponseNotAllowed
from django.utils.encoding import smart_str
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django_ajax.mixin import AJAXMixin
from django_datatables_view.base_datatable_view import BaseDatatableView

from ..core.utils import dict_merge


logger = logging.getLogger(__name__)


class RNINDatatablesPopulateView(BaseDatatableView):
    """ The base datatable population view for ResNet Internal datatables."""

    table_name = "datatable"
    data_source = None
    update_source = None
    form_class = None
    max_display_length = 200

    cached_forms = None

    column_definitions = OrderedDict()
    options = {
        "order": [[0, "asc"], [1, "asc"], [2, "asc"]],
        "language": {
            "search": "Filter records: ",
            "zeroRecords": "No records to display."
        },
        "processing": True,
        "serverSide": True,
        "lengthChange": False,

        "scrollX": True,
        "scrollY": "75vh",
        "deferRender": True,
        "scroller": True,
    }

    extra_options = {}

    base_column_template = """
        <div class='wrapper' column='{column}'>
            <div class='value-display' title='{value}'>
                {value}
                {link_block}
                {inline_images}
            </div>
            {editable_block}
        </div>
    """

    editable_block_template = """<input type='text' class='form-control editbox' value='{value}' />"""
    readonly_block_template = """<input type='text' class='form-control editbox' value='{value}' readonly="readonly" disabled="disabled" />"""
    link_block_template = """<a href='{link_url}' onclick='{onclick_action}' target='{link_target}' class='{link_class_name}' style='{link_style}'>{link_text}</a>"""
    icon_template = """<img src='{icon_url}' style='padding-left:5px;' align='top' width='16' height='16' border='0' />"""
    popover_link_block_template = """<a href='{link_url}' title='{popover_title}' popover-data-url='{content_url}' class='{link_class_name}' style='{link_style}'>{link_text}</a>"""

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
        return list(self.column_definitions.keys())

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
        """Get searchable columns and handle realated fields."""

        columns = self.get_columns()
        related_columns = self._get_columns_by_attribute("related", default=False)
        custom_lookup_columns = self._get_columns_by_attribute("custom_lookup", default=False)

        for column_name in columns:
            # If the column is related, append the lookup field to the column name
            if column_name in related_columns:
                related_column_name = column_name + "__" + self.column_definitions[column_name]["lookup_field"]
                columns[columns.index(column_name)] = related_column_name
            elif column_name in custom_lookup_columns:
                custom_lookup_field = self.column_definitions[column_name]["lookup_field"]
                columns[columns.index(column_name)] = custom_lookup_field

        return columns

    def get_searchable_columns(self):
        """Get searchable columns and handle realated fields."""

        searchable_columns = self._get_columns_by_attribute("searchable")
        related_columns = self._get_columns_by_attribute("related", default=False)
        custom_lookup_columns = self._get_columns_by_attribute("custom_lookup", default=False)

        for column_name in searchable_columns:
            # If the column is related, append the lookup field to the column name
            if column_name in related_columns:
                related_column_name = column_name + "__" + self.column_definitions[column_name]["lookup_field"]
                searchable_columns[searchable_columns.index(column_name)] = related_column_name
            elif column_name in custom_lookup_columns:
                custom_lookup_field = self.column_definitions[column_name]["lookup_field"]
                searchable_columns[searchable_columns.index(column_name)] = custom_lookup_field

        return searchable_columns

    def get_editable_columns(self):
        return self._get_columns_by_attribute("editable")

    def get_row_id(self, row):
        return str(row.id)

    def get_row_class(self, row):
        return None

    def get_row_data_attributes(self, row):
        return None

    def render_column(self, row, column):
        """Renders columns with customized HTML.

        :param row: A dictionary containing row data.
        :type row: dict
        :param column: The name of the column to be rendered. This can be used to index into the row dictionary.
        :type column: str
        :returns: The HTML to be displayed for this column.

        """

        raw_value = getattr(row, column)
        value = smart_str(raw_value) if raw_value else ""

        if not self.cached_forms:
            self.cached_forms = {}

        if row.id not in self.cached_forms:
            form = self.form_class(instance=row, auto_id="id_{id}-%s".format(id=row.id))
            self.cached_forms[row.id] = form
        else:
            form = self.cached_forms[row.id]

        if 'class' in form.fields[column].widget.attrs:
            form.fields[column].widget.attrs['class'] += " form-control editbox"
        else:
            form.fields[column].widget.attrs['class'] = " form-control editbox"

        if not(column in self.get_editable_columns() and self.get_write_permissions()):
            form.fields[column].widget.attrs['readonly'] = "readonly"
            form.fields[column].widget.attrs['disabled'] = "disabled"

        return self.base_column_template.format(column=column, value=value, link_block="", inline_images="", editable_block=str(form[column]))

    def prepare_results(self, qs):
        data = []

        for item in qs:
            row = {}
            row_id = self.get_row_id(item)
            row_class = self.get_row_class(item)
            row_data_attributes = self.get_row_data_attributes(item)

            if row_id:
                row.update({"DT_RowId": row_id})

            if row_class:
                row.update({"DT_RowClass": row_class})

            if row_data_attributes:
                row.update({"DT_RowAttr": row_data_attributes})

            for column in self.get_columns():
                row.update({str(self.get_columns().index(column)): self.render_column(item, column)})

            data.append(row)
        return data

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
            try:
                params = shlex.split(search_parameters)
            except ValueError:
                params = search_parameters.split(" ")
            column_q = Q()
            param_q = Q()

            for param in params:
                if param != "":
                    for searchable_column in searchable_columns:
                        column_q |= Q(**{searchable_column + "__icontains": param})

                    param_q.add(column_q, Q.AND)
                    column_q = Q()
            if param_q:
                qs = qs.filter(param_q)

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

        # Only one row is passed
        rendered_row = self.populate_class_instance.prepare_results([self.object])[0]

        context = {}
        context["form_valid"] = True
        context["rendered_row"] = rendered_row

        return context

    def form_invalid(self, form):
        form_errors = form.non_field_errors()
        field_errors = [field.errors for field in form if field.errors]

        context = {}
        context["form_valid"] = False

        context["fields_with_errors"] = [field.name for field in form if field.errors]
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
