"""
.. module:: resnet_internal.core.ajax
   :synopsis: ResNet Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import datetime
import logging

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax
from rmsconnector.constants import (SIERRA_MADRE, YOSEMITE, SOUTH_MOUNTAIN, NORTH_MOUNTAIN,
                                    CERRO_VISTA, POLY_CANYON_VILLAGE, SIERRA_MADRE_BUILDINGS, YOSEMITE_BUILDINGS,
                                    SOUTH_MOUNTAIN_BUILDINGS, NORTH_MOUNTAIN_BUILDINGS, CERRO_VISTA_BUILDINGS,
                                    POLY_CANYON_VILLAGE_BUILDINGS)

from .models import DailyDuties
from .utils import GetDutyData

logger = logging.getLogger(__name__)


@ajax
@require_POST
def update_building(request):
    """ Update building drop-down choices based on the community chosen.

    :param community: The community for which to display building choices.
    :type community: str
    :param building_selection: The building selected before form submission.
    :type building_selection: str

    """

    # Pull post parameters
    community = request.POST.get("community", None)
    building_selection = request.POST.get("building_selection", None)

    building_options = {
        SIERRA_MADRE: [(building, building) for building in SIERRA_MADRE_BUILDINGS],
        YOSEMITE: [(building, building) for building in YOSEMITE_BUILDINGS],
        SOUTH_MOUNTAIN: [(building, building) for building in SOUTH_MOUNTAIN_BUILDINGS],
        NORTH_MOUNTAIN: [(building, building) for building in NORTH_MOUNTAIN_BUILDINGS],
        CERRO_VISTA: [(building, building) for building in CERRO_VISTA_BUILDINGS],
        POLY_CANYON_VILLAGE: [(building, building) for building in POLY_CANYON_VILLAGE_BUILDINGS],
    }
    choices = []

    # Add options iff a building is selected
    if community:
        for value, label in building_options[str(community)]:
            if building_selection and value == building_selection:
                choices.append("<option value='%s' selected='selected'>%s</option>" % (value, label))
            else:
                choices.append("<option value='%s'>%s</option>" % (value, label))
    else:
        logger.debug("A building wasn't passed via POST.")
        choices.append("<option value='%s'>%s</option>" % ("", "---------"))

    data = {
        'inner-fragments': {
            '#id_building': ''.join(choices),
        },
    }

    return data


@ajax
def refresh_duties(request):

    # Load data dicts
    messages_dict = GetDutyData().get_messages()
    email_dict = GetDutyData().get_email()
    tickets_dict = GetDutyData().get_tickets() # {"count": 0, "status_color": "#900", "last_checked": "", "last_user": ""}

    if messages_dict["count"] > 0:
        message_count = u' <b>(' + str(messages_dict["count"]) + ')</b>'
    else:
        message_count = u''

    if email_dict["count"] >= 0:
        email_count = u' <b>(' + str(email_dict["count"]) + ')</b>'
    else:
        email_count = u''

    if tickets_dict["count"] > 0:
        ticket_count = u' <b>(' + str(tickets_dict["count"]) + ')</b>'
    else:
        ticket_count = u''

    duties_html = u"""
    <h2 class="center">Daily Duties</h2>
    <h3><a href='""" + reverse('phone_instructions') + """' class="popup_frame" style="cursor:pointer;" onclick="updateDuty('messages')">Check Messages""" + message_count + u"""</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + messages_dict["status_color"] + u"""'>""" + messages_dict["last_checked"] + u"""</font>
        <br />
        (""" + messages_dict["last_user"] + u""")
    </p>
    <h3><a href="/external/zimbra/" style="cursor:pointer;" target="_blank" onclick="updateDuty('email')">Check Email""" + email_count + u"""</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + email_dict["status_color"] + u"""'>""" + email_dict["last_checked"] + u"""</font>
        <br />
        (""" + email_dict["last_user"] + u""")
    </p>
    <h3><a href="/link_handler/srs/" style="cursor:pointer;" class="handler_link" onclick="updateDuty('tickets')">Check Tickets""" + ticket_count + u"""</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + tickets_dict["status_color"] + u"""'>""" + tickets_dict["last_checked"] + u"""</font>
        <br />
        (""" + tickets_dict["last_user"] + u""")
    </p>
    <h3></h3>
    <p>
        Note: Times update upon click of task title link.
    </p>"""

    data = {
        'inner-fragments': {
            '#dailyDuties': duties_html
        },
    }

    return data


@ajax
@require_POST
def update_duty(request):
    """ Update a particular duty.

    :param duty: The duty to update.
    :type duty: str

    """

    # Pull post parameters
    duty = request.POST["duty"]

    data = DailyDuties.objects.get(name=duty)
    data.last_checked = datetime.datetime.now()
    data.last_user = get_user_model().objects.get(username=request.user.username)
    data.save()

    return refresh_duties
