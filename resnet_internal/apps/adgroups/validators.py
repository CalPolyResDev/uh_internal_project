"""
.. module:: reslife_internal.adgroups.validators
   :synopsis: ResLife Internal AD Group Management Form Field Validators.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings
from django.core.exceptions import ValidationError
from ldap_groups import ADGroup
from ldap_groups.exceptions import AccountDoesNotExist


def validate_ad_membership(userPrincipalName):
    """ Check if the userPrincipalName is valid.

    :raises: **ValidationError** if the provided alias doesn't exist in the active directory.

    """

    try:
        ad_group_instance = ADGroup(settings.LDAP_GROUPS_BIND_DN)
        ad_group_instance._get_user_dn(userPrincipalName)
    except AccountDoesNotExist as message:
        raise ValidationError(message)
