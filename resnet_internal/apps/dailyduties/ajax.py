"""
.. module:: resnet_internal.apps.dailyduties.ajax
   :synopsis: ResNet Internal Daily Duties AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from collections import OrderedDict
from datetime import datetime

from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax

from .models import DailyDuties, VoicemailMessage
from .utils import GetDutyData
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView

logger = logging.getLogger(__name__)


@ajax
def refresh_duties(request):

    # Load data dicts
    printer_requests_dict = GetDutyData().get_printer_requests()
    messages_dict = GetDutyData().get_messages()
    email_dict = GetDutyData().get_email()
    tickets_dict = GetDutyData().get_tickets(request.user)

    if printer_requests_dict["count"] >= 0:
        printer_request_count = ' <b>(' + str(printer_requests_dict["count"]) + ')</b>'
    else:
        printer_request_count = ''

    if messages_dict["count"] >= 0:
        message_count = ' <b>(' + str(messages_dict["count"]) + ')</b>'
    else:
        message_count = ''

    if email_dict["count"] >= 0:
        email_count = ' <b>(' + str(email_dict["count"]) + ')</b>'
    else:
        email_count = ''

    if tickets_dict["count"] >= 0:
        ticket_count = ' <b>(' + str(tickets_dict["count"]) + ')</b>'
    else:
        ticket_count = ''

    duties_html = """
    <h2 class="center">Daily Duties</h2>
    <h3><a style="cursor:pointer;" onclick="updateDuty('printerrequests', '""" + reverse('printer_request_list') + """', '_self')">Check Printer Requests""" + printer_request_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + printer_requests_dict["status_color"] + """'>""" + printer_requests_dict["last_checked"] + """</font>
        <br />
        (""" + printer_requests_dict["last_user"] + """)
    </p>
    <h3><a href='""" + reverse('phone_instructions') + """' class="popup_frame" style="cursor:pointer;" onclick="updateDuty('messages', '', '_self')">Check Voicemail""" + message_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + messages_dict["status_color"] + """'>""" + messages_dict["last_checked"] + """</font>
        <br />
        (""" + messages_dict["last_user"] + """)
    </p>
    <h3><a style="cursor:pointer;" onclick="updateDuty('email', '/external/zimbra/', '_blank')">Check Email""" + email_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + email_dict["status_color"] + """'>""" + email_dict["last_checked"] + """</font>
        <br />
        (""" + email_dict["last_user"] + """)
    </p>
    <h3><a style="cursor:pointer;" onclick="updateDuty('tickets', '/link_handler/srs/', 'handler')">Check Tickets""" + ticket_count + """</a></h3>
    <p>
        Last Checked:
        <br />
        <font color='""" + tickets_dict["status_color"] + """'>""" + tickets_dict["last_checked"] + """</font>
        <br />
        (""" + tickets_dict["last_user"] + """)
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


class PopulateVoicemails(RNINDatatablesPopulateView):
    """Renders the voicemail list."""

    table_name = "voicemail_list"
    data_source = reverse_lazy('populate_voicemails')
    update_source = reverse_lazy('update_voicemails')
    model = VoicemailMessage

    column_definitions = OrderedDict()
    column_definitions["uuid"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "UUID"}
    column_definitions["sender"] = {"width": "225px", "searchable": False, "type": "string", "title": "Sender", "editable": False}
    column_definitions["date"] = {"width": "100px", "type": "string", "searchable": False, "title": "Date"}
    column_definitions["message"] = {"width": "100px", "type": "html", "searchable": False, "orderable": False, "editable": False, "title": "Message"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "Remove"}


    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"] = {"width": "50px", "type": "string", "searchable": False, "orderable": False, "editable": False, "title": "&nbsp;"}

        return super(PopulateVoicemails, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = False

    def render_column(self, row, column, class_names=None):
        if not class_names:
            class_names = []

        if column == 'message':
            try:
                audio_file_url = reverse_lazy('vm_attachment_request', kwargs={'uuid': row.uuid})
            except NoReverseMatch:
                return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value="", link_block="", inline_images="", editable_block="")
            else:
                audio_player = self.audio_template.format(link_url=audio_file_url, media_type="audio/wav")
                return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value=audio_player, link_block="", inline_images="", editable_block="")
        elif column == 'remove':
            onclick = "confirm_remove({id});return false;".format(id=row.uuid)
            link_block = self.link_block_template.format(link_url="", onclick_action=onclick, link_target="", link_class_name="", link_style="color:red; cursor:pointer;", link_text="Remove")

            return self.base_column_template.format(id=row.id, class_name=" ".join(class_names), column=column, value="", link_block=link_block, inline_images="", editable_block="")
        else:
            return super(PopulateVoicemails, self).render_column(row, column, class_names)


class UpdateVoicemails(BaseDatatablesUpdateView):
    model = VoicemailMessage
    populate_class = PopulateVoicemails


@ajax
@require_POST
def remove_vm(request):
    """ Removes computers from the computer index if no pinhole/domain name records are associated with it.

    :param vm_uuid: The vm's id.
    :type vm_uuid: int

    """

    # Pull post parameters
    vm_uuid = request.POST["vm_uuid"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["vm_uuid"] = vm_uuid

    dailyDuty = GetDutyData()
    dailyDuty.VoicemailUtilities.delete_message(vm_uuid)
    
    VoicemailMessage.objects.get(uuid=vm_uuid).delete()
    
    return context
