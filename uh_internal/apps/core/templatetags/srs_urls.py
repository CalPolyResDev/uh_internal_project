"""
.. module:: resnet_internal.apps.core.templatetags.srs_urls
   :synopsis: University Housing Internal SRS URLs.

.. moduleauthor:: Thomas Willson <thomas.willson@me.com>
"""

from django import template

register = template.Library()


@register.simple_tag
def srs_edit_url(ticket_id):
    return 'https://srs.calpoly.edu/gui2/cas-login?KB=calpoly2&state=Edit:helpdesk_case&record=' + str(ticket_id) + '&gui=Staff&record_access=Edit'
