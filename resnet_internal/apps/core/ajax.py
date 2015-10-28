"""
.. module:: resnet_internal.apps.core.ajax
   :synopsis: ResNet Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.views import ChainedSelectChoicesView
from datetime import datetime, timedelta
from operator import itemgetter
import logging

from django.template import Template, RequestContext
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax

from ..core.models import Community, Building, Room
from ..core.utils import NetworkReachabilityTester, get_ticket_list


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
                        <a href="https://calpoly.enterprisewizard.com/gui2/cas-login?KB=calpoly2&state=Edit:helpdesk_case&record={{ ticket.ticket_id }}&gui=Staff&record_access=Edit" target="_blank">
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
        return Building.objects.filter(community__id=self.parent_value)


class RoomChainedAjaxView(ChainedSelectChoicesView):

    def get_child_set(self):
        return Room.objects.filter(building__id=self.parent_value)
