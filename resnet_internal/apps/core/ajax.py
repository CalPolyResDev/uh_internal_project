"""
.. module:: resnet_internal.apps.core.ajax
   :synopsis: ResNet Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging
from operator import itemgetter

from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax

from ..core.models import Community
from ..core.utils import NetworkReachabilityTester

logger = logging.getLogger(__name__)


@ajax
@require_POST
def update_building(request):
    """ Update building drop-down choices based on the community chosen.

    :param community_id: The community for which to display building choices.
    :type community_id: str

    :param building_selection_id (optional): The building selected before form submission.
    :type building_selection_id (optional): str

    :param css_target (optional): The target of which to replace inner HTML. Defaults to #id_sub_department.
    :type css_target (optional): str

    """

    # Pull post parameters
    community_id = request.POST.get("community_id", None)
    building_selection_id = request.POST.get("building_selection_id", None)
    css_target = request.POST.get("css_target", '#id_sub_department')

    choices = []

    # Add options iff a department is selected
    if community_id:
        community_instance = Community.objects.get(id=int(community_id))

        for building in community_instance.buildings.all():
            if building_selection_id and building.id == int(building_selection_id):
                choices.append("<option value='{id}' selected='selected'>{name}</option>".format(id=building.id, name=building.name))
            else:
                choices.append("<option value='{id}'>{name}</option>".format(id=building.id, name=building.name))
    else:
        logger.warning("A department wasn't passed via POST.")
        choices.append("<option value='{id}'>{name}</option>".format(id="", name="---------"))

    data = {
        'inner-fragments': {
            css_target: ''.join(choices)
        },
    }

    return data


@ajax
def update_network_status(request):
    network_reachability_tester = NetworkReachabilityTester()
    
    network_reachability = network_reachability_tester.get_network_device_reachability()
    network_reachability.sort(key=itemgetter('status'))
    
    response_html = """
    <table class="dataTable">
        <tbody>
            <tr>
                <th scope="col">Name</th>
                <th scope="col">DNS Address</th>
                <th scope="col">IP Address</th>
                <th scope="col">Status</th>
            </tr>"""

    for reachability_result in network_reachability:
        print(reachability_result)
        response_html += """
                <tr id="reachability_""" + reachability_result['dns_name'] + """">
                    <td>""" + reachability_result['display_name'] + """</td>
                    <td>""" + reachability_result['dns_name'] + """</td>
                    <td>""" + reachability_result['ip_address'] + """</td>
                    <td style='color:""" + ("green" if reachability_result['status'] else "red") + ";'>" + ("UP" if reachability_result['status'] else "DOWN") + """</td>
                </tr>"""
    
    response_html += """
        </tbody>
    </table>
    """
    
    print(response_html)
    data = {
        'inner-fragments': {
            '#network_status_response': response_html
        },
    }

    return data
