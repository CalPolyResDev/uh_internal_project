"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

import re

from django.core.cache import cache
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView

from .utils import EmailManager


class EmailListView(TemplateView):
    template_name = "dailyduties/email.html"


class EmailMessageView(TemplateView):
    template_name = "dailyduties/email_viewer.html"

    def get_context_data(self, **kwargs):
        context = super(EmailMessageView, self).get_context_data(**kwargs)
        message_uid = kwargs['uid']
        mailbox_name = kwargs['mailbox_name']

        with EmailManager() as email_manager:
            message = email_manager.get_email_message(mailbox_name, message_uid)

        def _address_list_to_string(address_list):
            if not address_list:
                return ''

            return_string = ''

            for name, email in address_list:
                return_string += (name + ' <' + email + '>, ') if name else email + ', '

            return return_string[:-2]

        message['to'] = _address_list_to_string(message['to'])
        message['from'] = _address_list_to_string(message['from'])
        message['cc'] = _address_list_to_string(message['cc'])
        message['reply_to'] = _address_list_to_string(message['reply_to'])

        attachment_metadata = []

        for attachment in message['attachments']:
            print(attachment)
            metadata = {
                'filename': attachment[0],
                'size': len(attachment[1]),
            }
            attachment_metadata.append(metadata)

        message['attachments'] = attachment_metadata

        context['message'] = message
        return context


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
