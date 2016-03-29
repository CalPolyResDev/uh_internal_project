"""
.. module:: resnet_internal.apps.core.utils
   :synopsis: University Housing Internal Core Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from copy import deepcopy
from operator import itemgetter
import logging
import re

from django.core.cache import cache
from django.template.defaultfilters import slugify
from srsconnector.models import ServiceRequest


logger = logging.getLogger(__name__)


def dict_merge(base, merge):
    """ Recursively merges dictionaries.

    :param base: The base dictionary.
    :type base: dict
    :param merge: The dictionary to merge with base.
    :type merge: dict

    """

    if not isinstance(merge, dict):
        return merge
    result = deepcopy(base)

    for key, value in merge.items():
        if key in result and isinstance(result[key], dict):
            result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def get_ticket_list(user):
    user_teams = []
    if user.ad_groups.all().filter(display_name='UH TAG Member').exists():
        user_teams.append('SA University Housing')
    if user.ad_groups.all().filter(display_name='ResNet Technician').exists():
        user_teams.append('SA RESNET')

    cache_key = 'ticket_list:' + str(user_teams)

    tickets = cache.get(cache_key)

    if tickets is None:
        ticket_queryset = ServiceRequest.objects.filter(assigned_team__in=user_teams).exclude(status=4).exclude(status=8)

        tickets = list({'ticket_id': ticket.ticket_id,
                        'requestor_full_name': ticket.requestor_full_name,
                        'status': ticket.status,
                        'summary': ticket.summary,
                        'date_created': ticket.date_created,
                        'date_updated': ticket.date_updated,
                        'assigned_person': ticket.assigned_person,
                        'updater_is_technician': ticket.updater_is_technician,
                        'date_updated': ticket.date_updated,
                        } for ticket in ticket_queryset)

        tickets = sorted(tickets, key=itemgetter('date_created'), reverse=True)
        cache.set(cache_key, tickets, 60 * 5)

    return tickets


# Source for Slug methods: https://djangosnippets.org/snippets/690/
def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value
