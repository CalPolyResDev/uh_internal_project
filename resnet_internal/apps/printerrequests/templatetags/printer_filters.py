"""
.. module:: resnet_internal.apps.printerrequests.templatetags
   :synopsis: University Housing Internal Printer Request Template Tags and Filters.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django import template

from ..models import Request


register = template.Library()


@register.filter
def statusname(status_key):
    """ Returns a status value given a key.

    :param status_key: The key of the status to retrieve.
    :type status_key: str
    :returns: The value mapped the provided key in the
              STATUS_CHOICES list of the Request model.

    """

    return Request.STATUSES[status_key]


@register.filter
def commandstring(status):
    """ Returns a command string given a status.

    :param status: The key of the status to retrieve.
    :type status: str
    :returns: The command string associated with the provided status.

    """

    COMMANDS = ["Acknowledge", "Deliver", "Complete Request", ""]

    return COMMANDS[Request.STATUSES.index(status)]
