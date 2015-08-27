"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import re

from django.views.generic.base import TemplateView
from django.http.response import HttpResponse
from django.core.cache import cache

from .utils import EmailManager


class VoicemailListView(TemplateView):
    template_name = "dailyduties/voicemail_list.html"

    def get_context_data(self, **kwargs):
        context = super(VoicemailListView, self).get_context_data(**kwargs)

        with EmailManager() as email_manager:
            context["voicemails"] = email_manager.get_all_voicemail_messages()

        return context


class VoicemailAttachmentRequestView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        message_uid = self.kwargs["message_uid"]
        cached_file_data = cache.get('voicemail:' + message_uid)
        response = HttpResponse()

        if not cached_file_data:
            with EmailManager() as email_manager:
                filedata = email_manager.get_attachment(message_uid)[1]
            cache.set('voicemail:' + message_uid, filedata, 7200)
        else:
            filedata = cached_file_data

        # Safari Media Player does not like its range requests ignored so handle this.
        if self.request.META['HTTP_RANGE']:
            http_range_regex = re.compile('bytes=(\d*)-(\d*)$')
            regex_match = http_range_regex.match(self.request.META['HTTP_RANGE'])
            response_start = int(regex_match.groups()[0])
            response_end = int(regex_match.groups()[1] if regex_match.groups()[1] else (len(filedata) - 1))
        else:
            response_start = 0
            response_end = len(filedata) - 1

        response.write(filedata[response_start:response_end + 1])
        response["Accept-Ranges"] = 'bytes'
        response["Content-Length"] = response_end - response_start + 1
        response["Content-Type"] = 'audio/wav'
        response["Content-Range"] = 'bytes ' + str(response_start) + '-' + str(response_end) + '/' + str(len(filedata))

        return response
