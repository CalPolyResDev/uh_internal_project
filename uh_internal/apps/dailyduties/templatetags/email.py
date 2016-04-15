"""
.. module:: uh_internal.apps.dailyduties.templatetags.email
   :synopsis: University Housing Internal Daily Duties Email Template Tags

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from django.template import Library
from django.utils.html import escapejs

register = Library()


@register.simple_tag(takes_context=True)
def email_record_onclick(context):
    message_properties = {
        'full_id': context['email']['full_id'],
        'mailbox_name': context['email']['mailbox'],
        'uid': context['email']['uid'],
        'modal_title': context['email']['modal_title'],
    }

    for k, v in message_properties.items():
        message_properties[k] = escapejs(v)

    return 'open_email("{mailbox_name}", "{uid}", "{full_id}", "{modal_title}");'.format(**message_properties)
