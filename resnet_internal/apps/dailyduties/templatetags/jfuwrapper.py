'''
Created on Sep 30, 2015

@author: thomaswillson
'''
from django.template import Library
from django.utils.html import escapejs
from jfu.templatetags.jfutags import jfu

register = Library()


@register.simple_tag(takes_context=True)
def jfu_escaped(
    context,
    template_name='jfu/upload_form.html',
    upload_handler_name='jfu_upload',
    *args, **kwargs
):

    jfu_response = jfu(context, template_name, upload_handler_name, *args, **kwargs)
    return escapejs(jfu_response)
