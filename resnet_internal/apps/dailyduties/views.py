"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from resnet_internal.apps.dailyduties.utils import GetDutyData, VoicemailManager

from django.views.generic.base import TemplateView
from django.http.response import HttpResponse


class PhoneInstructionsView(TemplateView):
    template_name = "dailyduties/phone_message_instructions.html"
    
    def get_context_data(self, **kwargs):
        context = super(PhoneInstructionsView, self).get_context_data(**kwargs)
        
        voicemail = VoicemailManager()
        context["voicemails"] = voicemail.get_all_voicemail()
        return context


class VoicemailAttachmentRequestView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        voicemail = VoicemailManager()
        filedata = voicemail.get_attachment_uuid(context["uuid"])[1]

        response = HttpResponse(content_type='audio/wav')
        response.write(filedata)
        response['Content-Length'] = filedata.length

        return response
