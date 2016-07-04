"""
.. module:: resnet_internal.technicians.validators
   :synopsis: University Housing Internal Technicians Form Field Validators.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.conf import settings
from django.core.exceptions import ValidationError
from ldap_groups import ADGroup
from ldap_groups.exceptions import AccountDoesNotExist


def validate_ad_membership(user_principal_name):
    """ Check if the userPrincipalName is valid.

    :raises: **ValidationError** if the provided alias doesn't exist in the active directory.

    """

    try:
        ad_group_instance = ADGroup(settings.LDAP_GROUPS_BIND_DN)
        ad_group_instance._get_user_dn(user_principal_name)
    except AccountDoesNotExist as message:
        raise ValidationError(message)
