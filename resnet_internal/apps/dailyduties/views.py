"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from resnet_internal.apps.dailyduties.utils import VoicemailManager

from django.views.generic.base import TemplateView
from django.http.response import HttpResponse
from django.core.cache import cache


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
        cached_filedata = cache.get('vm_' + uuid)
        
        if (cached_filedata is None):
            with VoicemailManager() as voicemail_manager:
                    filedata = voicemail_manager.get_attachment_uuid(uuid)[1]
            cache.set('vm_' + uuid, filedata, 7200)
            print('Saving to Cache')
        else:
            filedata = cached_filedata
            print('Loading from Cache')

        response = HttpResponse()
        
        for key, value in self.request.META.items():
            if key.startswith('HTTP'):
                print(key + ': ' + value)
         
        # Safari Media Player does not like its range requests
        # ignored so handle this in a primitive way.
        if self.request.META['HTTP_RANGE'] == 'bytes=0-1':
            response.write([b'\xDE\xAD'])
            response_length = 2
        else:
            response.write(filedata)
            response_length = len(filedata)

        response["Accept-Ranges"] = 'bytes'
        response["Content-Length"] = response_length
        response["Content-Type"] = 'audio/wav'
        response["Content-Range"] = 'bytes 0-' + str(response_length - 1) + '/' + str(len(filedata))
        
        print(response.serialize_headers())

        return response
