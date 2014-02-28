"""
.. module:: resnet_internal.core.ajax
   :synopsis: ResNet Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import datetime
import imaplib

from django.conf import settings
from django.contrib.auth import get_user_model

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from srsconnector.models import ServiceRequest
from rmsconnector.constants import (SIERRA_MADRE, YOSEMITE, SOUTH_MOUNTAIN, NORTH_MOUNTAIN,
                                    CERRO_VISTA, POLY_CANYON_VILLAGE, SIERRA_MADRE_BUILDINGS, YOSEMITE_BUILDINGS,
                                    SOUTH_MOUNTAIN_BUILDINGS, NORTH_MOUNTAIN_BUILDINGS, CERRO_VISTA_BUILDINGS,
                                    POLY_CANYON_VILLAGE_BUILDINGS)

from .models import DailyDuties

GREEN = "#060"
RED = "#900"

ACCEPTABLE_LAST_CHECKED = datetime.timedelta(days=1)


@dajaxice_register
def update_building(request, community):
    """ Update building drop-down choices based on the community chosen.

    :param community: The community for which to display building choices.
    :type community: str

    """

    dajax = Dajax()

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
    if str(community) != "":
        for value, label in building_options[str(community)]:
            choices.append("<option value='%s'>%s</option>" % (value, label))
    else:
        choices.append("<option value='%s'>%s</option>" % ("", "-------------"))

    dajax.assign('#id_building', 'innerHTML', ''.join(choices))

    return dajax.json()


@dajaxice_register
def refresh_duties(request):
    dajax = Dajax()

    # Load data dicts
    messages_dict = GetDutyData().get_messages()
    email_dict = GetDutyData().get_email()
    tickets_dict = GetDutyData().get_tickets()

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
    <h3><a style="cursor:pointer;" onclick="updateDuty('messages')">Check Messages""" + message_count + u"""</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + messages_dict["status_color"] + u"""'>""" + messages_dict["last_checked"] + u"""</font>
        <br />
        (""" + messages_dict["last_user"] + u""")
    </p>
    <h3><a style="cursor:pointer;" onclick="updateDuty('email')">Check Email""" + email_count + u"""</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + email_dict["status_color"] + u"""'>""" + email_dict["last_checked"] + u"""</font>
        <br />
        (""" + email_dict["last_user"] + u""")
    </p>
    <h3><a style="cursor:pointer;" onclick="updateDuty('tickets')">Check Tickets""" + ticket_count + u"""</a></h3>
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

    # Update the daily duties widget
    dajax.assign('#dailyDuties', 'innerHTML', duties_html)

    return dajax.json()


@dajaxice_register
def update_duty(request, duty):
    dajax = Dajax()

    data = DailyDuties.objects.get(name=duty)
    data.last_checked = datetime.datetime.now()
    data.last_user = get_user_model().objects.get(username=request.user.username)
    data.save()

    return dajax.json()


class GetDutyData:

    def get_messages(self):
        """Checks the current number of voicemail messages.

        An API for this has not been discovered yet; For now this method always returns zero.

        """

        messages = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        data = DailyDuties.objects.get(name='messages')

        messages["count"] = 0
        if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
            messages["status_color"] = GREEN
        else:
            messages["status_color"] = RED
        messages["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
        messages["last_user"] = data.last_user.get_full_name()

        return messages

    def get_email(self):
        """Checks the current number of unread email messages."""

        email = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }
        server = None

        # Connect to the email server and authenticate
        if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
            server = imaplib.IMAP4_SSL(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
        else:
            server = imaplib.IMAP4(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
        server.login(settings.INCOMING_EMAIL['IMAP4']['USER'], settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])

        # Grab the number of unread emails
        server.select('inbox', readonly=True)  # Select the Inbox
        r, search_data = server.search(None, "UnSeen")  # Search for unread emails
        unread_count = len(search_data[0].split())  # Count unread emails
        server.logout()  # Disconnect from the email server

        data = DailyDuties.objects.get(name='email')

        email["count"] = unread_count
        if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
            email["status_color"] = GREEN
        else:
            email["status_color"] = RED
        email["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
        email["last_user"] = data.last_user.get_full_name()

        return email

    def get_tickets(self):
        """Checks the current number of queued SRS tickets."""

        tickets = {
            "count": None,
            "status_color": None,
            "last_checked": None,
            "last_user": None
        }

        open_tickets = ServiceRequest.objects.filter(assigned_team="SA RESNET").exclude(status=4).count()
        api_tickets = ServiceRequest.objects.filter(assigned_person="ResnetAPI").count()

        data = DailyDuties.objects.get(name='tickets')

        tickets["count"] = open_tickets - api_tickets
        if data.last_checked > datetime.datetime.now() - ACCEPTABLE_LAST_CHECKED:
            tickets["status_color"] = GREEN
        else:
            tickets["status_color"] = RED
        tickets["last_checked"] = datetime.datetime.strftime(data.last_checked, "%m/%d/%Y %H:%M%p")
        tickets["last_user"] = data.last_user.get_full_name()

        return tickets
