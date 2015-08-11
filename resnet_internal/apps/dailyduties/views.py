"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from resnet_internal.apps.datatables.views import DatatablesView
from resnet_internal.apps.dailyduties.ajax import PopulateVoicemails
from resnet_internal.apps.dailyduties.models import VoicemailMessage
from resnet_internal.apps.dailyduties.utils import GetDutyData

from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.http.response import HttpResponse


class PhoneInstructionsView(DatatablesView):
    template_name = "core/phone_message_instructions.html"
    form_class = None
    populate_class = PopulateVoicemails
    model = VoicemailMessage
    success_url = reverse_lazy('uh_voicemails')


class VMAttachmentRequestView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        dutyData = GetDutyData()
        filedata = dutyData.VoicemailUtilities.get_attachment_uuid(context["uuid"])[1]

        response = HttpResponse(content_type='audio/wav')
        response.write(filedata)
        response['Content-Length'] = filedata.length

        return response
