"""
.. module:: resnet_internal.apps.dailyduties.views
   :synopsis: ResNet Internal DailyDuties Views.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from os import path
import re

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.templatetags.static import static
from django.views.generic.base import TemplateView

from .utils import EmailManager, get_archive_folders


class EmailListView(TemplateView):
    template_name = "dailyduties/email.html"

    def get_context_data(self, **kwargs):
        context = super(EmailListView, self).get_context_data(**kwargs)

        context['archive_folders'] = get_archive_folders()

        return context


class EmailMessageView(TemplateView):
    template_name = "dailyduties/email_viewer.html"

    def get_context_data(self, **kwargs):
        context = super(EmailMessageView, self).get_context_data(**kwargs)
        message_uid = kwargs['uid']
        mailbox_name = kwargs['mailbox_name']

        with EmailManager() as email_manager:
            message = email_manager.get_email_message(mailbox_name, message_uid)
            email_manager.mark_message_read(mailbox_name, message_uid)

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

        attachment_icons = ['accdb', 'avi', 'csv', 'doc', 'docx', 'mp4', 'mpeg', 'pdf', 'pps', 'ppt', 'pptx', 'rtf', 'swf', 'txt', 'xls', 'xlsx']
        attachment_metadata = []

        for attachment in message['attachments']:
            extension = path.splitext(attachment['filename'])[1][1:]
            metadata = {
                'filename': attachment['filename'],
                'size': len(attachment['filedata']),
                'icon': static('images/attachment_icons/' + extension + '-icon.png') if extension in attachment_icons else static('images/attachment_icons/default.png'),
                'url': reverse('email_get_attachment', kwargs={'uid': message_uid,
                                                               'mailbox_name': mailbox_name,
                                                               'attachment_index': message['attachments'].index(attachment)})
            }
            attachment_metadata.append(metadata)
        message['attachments'] = attachment_metadata

        quote_string = "On " + message['date'].strftime('%b %d, %Y at %I:%M%p') + ", " + message['from'] + " wrote:"

        if message['is_html']:
            reply_html = message['body_html']

            if reply_html.find('<body>') >= 0:
                reply_html = reply_html.replace('<body>', '<body><p id="new_body"><br /><br />Best regards,<br />' + self.request.user.get_full_name() + '<br />ResNet Technician</p><div><div>' + quote_string + '<div><div><blockquote>').replace('</body>', '</blockquote></body>')
            else:
                reply_html = '<p id="start_message"><br /><br />Best regards,<br />' + self.request.user.get_full_name() + '<br />ResNet Technician</p><div><div>' + '<blockquote>\n' + quote_string + reply_html + '\n</blockquote>'

            message['reply_html'] = reply_html
        else:
            reply_text = message['body_plain_text']
            reply_text = '>'.join(reply_text.splitlines(True))
            reply_text = '\n\n\nBest regards,\n' + self.request.user.get_full_name() + '\nResNet Technician\n\n>' + quote_string + '\n\n>' + reply_text
            message['reply_plain_text'] = reply_text

        context['message'] = message
        context['archive_folders'] = get_archive_folders()
        return context


class EmailAttachmentRequestView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        message_uid = context['uid']
        mailbox_name = context['mailbox_name']

        if 'attachment_index' in context:
            attachment_index = context['attachment_index']
        elif 'content_id' in context:
            content_id = '<' + context['content_id'] + '>'

        with EmailManager() as email_manager:
            message = email_manager.get_email_message(mailbox_name, message_uid)

        if attachment_index:
            attachment = message['attachments'][int(attachment_index)]
        elif content_id:
            attachment = next(attachment for attachment in message['attachments'] if attachment['content-id'] == content_id)
        else:
            Exception('No form of attachment id provided.')

        response = HttpResponse()

        if 'HTTP_RANGE' in self.request.META:
            http_range_regex = re.compile('bytes=(\d*)-(\d*)$')
            regex_match = http_range_regex.match(self.request.META['HTTP_RANGE'])
            response_start = int(regex_match.groups()[0])
            response_end = int(regex_match.groups()[1] if regex_match.groups()[1] else (len(attachment['filedata']) - 1))
        else:
            response_start = 0
            response_end = len(attachment['filedata']) - 1

        response.write(attachment['filedata'][response_start:response_end + 1])
        response["Accept-Ranges"] = 'bytes'
        response["Content-Length"] = response_end - response_start + 1
        response["Content-Type"] = attachment['filetype']
        response["Content-Range"] = 'bytes ' + str(response_start) + '-' + str(response_end) + '/' + str(len(attachment['filedata']))
        response["Content-Disposition"] = 'filename="' + str(attachment['filename']) + '"'

        return response


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
                email_manager.mark_message_read('Voicemails', message_uid)
                filedata = email_manager.get_voicemail_attachment(message_uid)[1]

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
