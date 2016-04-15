"""
.. module:: resnet_internal.apps.dailyduties.urls
   :synopsis: University Housing Internal Daily Duties URLs

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from ..core.permissions import daily_duties_access
from .ajax import (email_archive, email_mark_read, email_mark_unread, get_csd_email, get_email_folders, get_mailbox_summary,
                   send_email, attachment_delete, attachment_upload, remove_voicemail, ticket_from_email, refresh_duties, update_duty,
                   EmailAmViewing, EmailStoppedViewing, EmailWhoIsViewing)
from .views import EmailAttachmentRequestView, EmailComposeView, EmailListView, EmailMessageView, VoicemailListView, VoicemailAttachmentRequestView, EmailMessagePermalinkView


app_name = 'dailyduties'

urlpatterns = [
    url(r'^email/list/$', login_required(daily_duties_access(EmailListView.as_view())), name='email_list'),
    url(r'^email/view/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/$', login_required(daily_duties_access(EmailMessageView.as_view())), name='email_view_message'),
    url(r'^email/permalink/view/(?P<slug>.+)/$', login_required(daily_duties_access(EmailMessagePermalinkView.as_view())), name='email_permalink_view_message'),
    url(r'^email/compose/$', login_required(daily_duties_access(EmailComposeView.as_view())), name='email_compose'),
    url(r'^email/mark_unread/$', login_required(daily_duties_access(email_mark_unread)), name='email_mark_unread'),
    url(r'^email/mark_read/$', login_required(daily_duties_access(email_mark_read)), name='email_mark_read'),
    url(r'^email/archive$', login_required(daily_duties_access(email_archive)), name='email_archive'),
    url(r'^email/get_attachment/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/(?P<attachment_index>[0-9]+)/$', login_required(daily_duties_access(EmailAttachmentRequestView.as_view())), name='email_get_attachment'),
    url(r'^email/get_attachment/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/(?P<content_id>[^<>]+)/$', login_required(daily_duties_access(EmailAttachmentRequestView.as_view())), name='email_get_attachment'),
    url(r'^email/get_folders/$', login_required(daily_duties_access(get_email_folders)), name='email_get_folders'),
    url(r'^email/get_mailbox_summary/(?P<mailbox_name>.*)/(?P<search_string>.*)/(?P<message_group>[0-9]+)/$', login_required(daily_duties_access(get_mailbox_summary)), name='email_get_mailbox_summary_range'),
    url(r'^email/get_mailbox_summary/(?P<mailbox_name>.*)/(?P<search_string>.*)/$', login_required(daily_duties_access(get_mailbox_summary)), name='email_get_mailbox_summary'),
    url(r'^email/send_email/$', login_required(daily_duties_access(send_email)), name='send_email'),
    url(r'^email/upload_attachment/$', daily_duties_access(attachment_upload), name='jfu_upload'),
    url(r'^email/delete_attachment/(?P<pk>.+)$', daily_duties_access(attachment_delete), name='jfu_delete'),
    url(r'^email/cc_csd/$', daily_duties_access(get_csd_email), name='email_get_cc_csd'),
    url(r'^email/create_ticket/$', login_required(daily_duties_access(ticket_from_email)), name='email_create_ticket'),
    url(r'^email/am_viewing/(?P<message_path>.+)/(?P<replying>0|1)/$', login_required(daily_duties_access(EmailAmViewing.as_view())), name='email_am_viewing'),
    url(r'^email/stopped_viewing/(?P<message_path>.+)/$', login_required(daily_duties_access(EmailStoppedViewing.as_view())), name='email_stopped_viewing'),
    url(r'^email/viewer_list/$', login_required(daily_duties_access(EmailWhoIsViewing.as_view())), name="email_who_is_viewing"),

    url(r'^voicemail_list/$', login_required(daily_duties_access(VoicemailListView.as_view())), name='voicemail_list'),
    url(r'^refresh_duties/$', login_required(daily_duties_access(refresh_duties)), name='refresh_duties'),
    url(r'^update_duty/$', login_required(daily_duties_access(update_duty)), name='update_duty'),
    url(r"^voicemail/(?P<message_uid>\b[0-9]+\b)/$", login_required(daily_duties_access(VoicemailAttachmentRequestView.as_view())), name='voicemail_attachment_request'),
    url(r"^remove_voicemail/$", login_required(daily_duties_access(remove_voicemail)), name='remove_voicemail'),
]
