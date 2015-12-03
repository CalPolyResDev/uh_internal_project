"""
.. module:: resnet_internal.apps.core.ajax
   :synopsis: ResNet Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.views import ChainedSelectChoicesView
from collections import OrderedDict
from datetime import datetime, timedelta
from operator import itemgetter
import logging

from django.core.urlresolvers import reverse_lazy
from django.template import Template, RequestContext
from django_ajax.decorators import ajax

from ...settings.base import technician_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView
from .forms import RoomUpdateForm
from .models import Building, Room
from .utils import NetworkReachabilityTester, get_ticket_list


logger = logging.getLogger(__name__)


@ajax
def update_network_status(request):
    network_reachability = NetworkReachabilityTester.get_network_device_reachability()
    network_reachability.sort(key=itemgetter('status', 'display_name'))

    raw_response = """
        <table class="dataTable">
            <tbody>
                <tr>
                    <th scope="col">Name</th>
                    {% if request.user.is_authenticated %}
                    <th scope="col">DNS Address</th>
                    <th scope="col">IP Address</th>
                    {% endif %}
                    <th scope="col">Status</th>
                </tr>
                {% for reachability_result in network_reachability %}
                <tr id="reachability_{% ">
                        <td>{{ reachability_result.display_name }}</td>
                        {% if request.user.is_authenticated %}
                        <td>{{ reachability_result.dns_name }}</td>
                        <td>{{ reachability_result.ip_address }}</td>
                        {% endif %}
                        <td style='color:{% if reachability_result.status %}green;'>UP{% else %}red;'>DOWN{% endif %}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        """

    template = Template(raw_response)
    context = RequestContext(request, {'network_reachability': network_reachability})
    response_html = template.render(context)

    data = {
        'inner-fragments': {
            '#network_status_response': response_html
        },
    }

    return data


@ajax
def get_tickets(request):
    raw_response = """
        {% load staticfiles %}
        {% load core_filters %}
        {% load srs_urls %}
        <table class="dataTable">
            <tbody>
                <tr>
                    <th scope="col"></th>
                    <th scope="col"></th>
                    <th scope="col">Name</th>
                    <th scope="col">Status</th>
                    <th scope="col">Summary</th>
                </tr>
                {% for ticket in tickets %}
                <tr id="ticket_{{ ticket.ticket_id }}" class={{ ticket.display_class }}>
                    <td>
                        <a href="{% url 'core_ticket_summary' ticket_id=ticket.ticket_id %}" class="popup_frame" style="cursor:pointer;">
                            <img src="{% static 'images/srs_view_button.gif' %}">
                        </a>
                    </td>
                    <td>
                        <a href="{% srs_edit_url ticket.ticket_id %}" target="_blank">
                            <img src="{% static 'images/srs_edit_button.gif' %}">
                        </a>
                    </td>
                    <td>{{ ticket.requestor_full_name }}</td>
                    <td>{{ ticket.status }}</td>
                    <td>{{ ticket.summary|clean_srs_escapes }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>"""

    tickets = get_ticket_list(request.user)
    now = datetime.today()

    tickets[:] = [ticket for ticket in tickets if ticket['assigned_person'].strip() != 'ResnetAPI']

    for ticket in tickets:
        if ((not ticket['assigned_person'] or ticket['assigned_person'] == request.user.get_full_name()) and
                (ticket['status'] != 'Pending Information' or ticket['updater_is_technician'] == False or
                 ticket['date_updated'] + timedelta(weeks=1) < datetime.today())):

            time_difference = (now - ticket['date_updated']).total_seconds() / 86400
            if time_difference < 3:
                ticket['display_class'] = 'bg-success'
                ticket['sort_order'] = 1
            elif time_difference < 7:
                ticket['display_class'] = 'bg-info'
                ticket['sort_order'] = 2
            elif time_difference < 14:
                ticket['display_class'] = 'bg-warning'
                ticket['sort_order'] = 3
            else:
                ticket['display_class'] = 'bg-danger'
                ticket['sort_order'] = 4
        else:
            ticket['display_class'] = 'bg-muted'
            ticket['sort_order'] = 5

    tickets.sort(key=itemgetter('sort_order'))
    template = Template(raw_response)
    context = RequestContext(request, {'tickets': tickets})
    response_html = template.render(context)

    data = {
        'inner-fragments': {
            '#tickets_response': response_html
        }
    }

    return data


class BuildingChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Building.objects.filter(community__id=self.parent_value).order_by('name')


class RoomChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Room.objects.filter(building__id=self.parent_value).order_by('name')


class PopulateResidenceHallRooms(RNINDatatablesPopulateView):
    """Renders the room listing."""

    table_name = "residence_halls_rooms"
    data_source = reverse_lazy('populate_residence_halls_rooms')
    update_source = reverse_lazy('update_residence_halls_room')
    model = Room
    max_display_length = 1000

    column_definitions = OrderedDict()
    column_definitions["id"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "ID"}
    column_definitions["community"] = {"width": "100px", "type": "string", "editable": False, "title": "Community", "custom_lookup": True, "lookup_field": "building__community__name"}
    column_definitions["building"] = {"width": "100px", "type": "string", "editable": False, "title": "Building", "related": True, "lookup_field": "name"}
    column_definitions["name"] = {"width": "55px", "type": "string", "className": "edit_trigger", "title": "Name"}

    extra_options = {
        "language": {
            "lengthMenu":
                'Display <select>' +
                '<option value="50">50</option>' +
                '<option value="100">100</option>' +
                '<option value="250">250</option>' +
                '<option value="500">500</option>' +
                '<option value="1000">1000</option>' +
                '<option value="-1">All</option>' +
                '</select> records:',
            "search": "Filter records:",
        },
    }

    def _initialize_write_permissions(self, user):
        self.write_permissions = technician_access_test(user)

    def render_column(self, row, column, class_names=None):
        if not class_names:
            class_names = []

        if column in self.get_editable_columns() and self.get_write_permissions():
            value = getattr(row, column)
            editable_block = self.editable_block_template.format(value=value)
            class_names.append("editable")

            return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
        else:
            return super(PopulateResidenceHallRooms, self).render_column(row, column, class_names)


class UpdateResidenceHallRoom(BaseDatatablesUpdateView):
    form_class = RoomUpdateForm
    model = Room
    populate_class = PopulateResidenceHallRooms
