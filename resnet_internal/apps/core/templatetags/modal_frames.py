"""
.. module:: resnet_internal.apps.core.templatetags.srs_urls
   :synopsis: ResNet Internal SRS URLs.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>
"""

from django import template

register = template.Library()


@register.inclusion_tag('core/modal_frame.html')
def modal_frame(modal_title, modal_id):
    return {'modal_id': modal_id, 'modal_title': modal_title}


@register.inclusion_tag('core/modal_frame_support.html')
def modal_frame_support():
    return {}
