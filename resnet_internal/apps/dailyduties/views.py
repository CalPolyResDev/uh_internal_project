"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from resnet_internal.apps.dailyduties.utils import VoicemailManager

from django.views.generic.base import TemplateView
from django.http.response import FileResponse


class PhoneInstructionsView(TemplateView):
    template_name = "dailyduties/phone_message_instructions.html"
    
    def get_context_data(self, **kwargs):
        context = super(PhoneInstructionsView, self).get_context_data(**kwargs)
        
        with VoicemailManager() as voicemail_manager:
            context["voicemails"] = voicemail_manager.get_all_voicemail()
        
        return context


class VoicemailAttachmentRequestView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        uuid = self.kwargs["uuid"]
        
        with VoicemailManager() as voicemail_manager:
            filedata = voicemail_manager.get_attachment_uuid(uuid)[1]

        response = FileResponse(filedata, content_type='audio/wav')

        return response
