"""
.. module:: resnet_internal.apps.core.ajax
   :synopsis: University Housing Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict
from datetime import datetime, timedelta
from operator import itemgetter
import ast
import logging

from clever_selects.views import ChainedSelectChoicesView
from django.core.urlresolvers import reverse_lazy
from django.template import Template, RequestContext
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax

from ...settings.base import technician_access_test
from ..datatables.ajax import RNINDatatablesPopulateView, RNINDatatablesFormView, BaseDatatablesUpdateView
from .forms import RoomCreateForm, RoomUpdateForm
from .models import Building, Room, SubDepartment, CSDMapping
from .utils import NetworkReachabilityTester, get_ticket_list


logger = logging.getLogger(__name__)


@ajax
def update_network_status(request):
    network_reachability = NetworkReachabilityTester.get_network_device_reachability(2)
    network_reachability.sort(key=itemgetter('status', 'display_name'))

    raw_response = """
        <table class="table table-hover table-striped table-condensed">
            <thead>
                <tr>
                    <th>Name</th>
                    {% if request.user.is_authenticated %}
                    <th>DNS Address</th>
                    <th>IP Address</th>
                    {% endif %}
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for reachability_result in network_reachability %}
                <tr>
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
            '#network-status-response': response_html
        },
    }

    return data


@ajax
def get_tickets(request):
    raw_response = """
        {% load staticfiles %}
        {% load core_filters %}
        {% load srs_urls %}
        <table class="table table-condensed">
            <thead>
                <tr>
                    <th></th>
                    <th></th>
                    <th>Requestor</th>
                    <th>Status</th>
                    <th>Summary</th>
                </tr>
            </thead>
            <tbody>
                {% for ticket in tickets %}
                <tr id="ticket_{{ ticket.ticket_id }}" class={{ ticket.display_class }}>
                    <td>
                        <a onclick="openModalFrame('Ticket Summary', '{% url 'core_ticket_summary' ticket_id=ticket.ticket_id %}');" style="cursor:pointer;">
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

    now = datetime.today()

    tickets = [ticket for ticket in get_ticket_list(request.user) if ticket['assigned_person'].strip() != 'ResnetAPI']

    for ticket in tickets:
        if ((not ticket['assigned_person'] or ticket['assigned_person'] == request.user.get_full_name()) and
                (ticket['status'] != 'Pending Information' or ticket['updater_is_technician'] == False or
                 ticket['date_updated'] + timedelta(weeks=1) < datetime.today())):

            time_difference = (now - ticket['date_updated']).total_seconds() / 86400  # 24 hours
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

        ticket['modal_id'] = 'ticket_' + ticket['ticket_id']

    tickets.sort(key=itemgetter('sort_order'))
    template = Template(raw_response)
    context = RequestContext(request, {'tickets': tickets})
    response_html = template.render(context)

    data = {
        'inner-fragments': {
            '#tickets-response': response_html
        }
    }

    return data


@ajax
@require_POST
def update_csd_domain(request):
    """Updates a csd domain mapping.

    :param mapping_id: The mapping id.
    :type mapping_id: int
    :param csd_info: The updated info for the mapping.
    :type csd_info: dict

    """

    # Pull post parameters
    mapping_id = request.POST["mapping_id"]
    csd_info_dict = ast.literal_eval(request.POST["csd_info"])
    csd_name = csd_info_dict['name']
    csd_email = csd_info_dict['email']

    csd_mapping = CSDMapping.objects.get(id=mapping_id)
    csd_mapping.name = csd_name
    csd_mapping.email = csd_email
    csd_mapping.save()

    data = {
        'inner-fragments': {
            "#row_{id}_name".format(id=mapping_id): csd_name,
            "#row_{id}_email".format(id=mapping_id): csd_email,
        },
    }

    return data


class BuildingChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Building.objects.filter(community__id=self.parent_value).order_by('name')


class RoomChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Room.objects.filter(building__id=self.parent_value).order_by('name')


class SubDepartmentChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return SubDepartment.objects.filter(department__id=self.parent_value).order_by('name')


class PopulateRooms(RNINDatatablesPopulateView):
    """Renders the room listing."""

    table_name = "rooms"

    data_source = reverse_lazy('populate_rooms')
    update_source = reverse_lazy('update_room')
    form_source = reverse_lazy('form_room')

    form_class = RoomCreateForm
    model = Room

    item_name = 'room'
    remove_url_name = 'remove_room'

    column_definitions = OrderedDict()
    column_definitions["community"] = {"type": "string", "editable": False, "title": "Community", "custom_lookup": True, "lookup_field": "building__community__name"}
    column_definitions["building"] = {"type": "string", "editable": False, "title": "Building", "related": True, "lookup_field": "name"}
    column_definitions["name"] = {"type": "string", "title": "Name"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "scrollX": False,
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"] = {"width": "80px", "type": "string", "searchable": False, "editable": False, "title": "&nbsp;"}

        return super().get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = technician_access_test(user)


class RetrieveRoomForm(RNINDatatablesFormView):
    populate_class = PopulateRooms


class UpdateRoom(BaseDatatablesUpdateView):
    form_class = RoomUpdateForm
    model = Room
    populate_class = PopulateRooms
