"""
.. module:: reslife_internal.adgroups.validators
   :synopsis: ResLife Internal AD Group Management Form Field Validators.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.core.exceptions import ValidationError, ObjectDoesNotExist

from ldap_groups import ADGroup

from django.conf import settings


def validate_ad_membership(alias):
    """ Check if the alias is valid.

    :raises: **ValidationError** if the provided alias doesn't exist in the active directory.

    """

    try:
        ad_group_instance = ADGroup(settings.AUTH_LDAP_BIND_DN)
        ad_group_instance._get_user_dn(alias)
    except ObjectDoesNotExist as message:
        raise ValidationError(message)
