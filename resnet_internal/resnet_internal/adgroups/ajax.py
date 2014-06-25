"""
.. module:: reslife_internal.adgroups.ajax
   :synopsis: ResLife Internal AD Group Management AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from ldap_groups import ADGroup
from srsconnector.models import AccountRequest


@dajaxice_register
def remove_member(request, account_name, group_dn):
    """ Removes members from an active directory group.

    :param account_name: The member's account name.
    :type account_name: str
    :param group_dn: The distinguished name of the active directory group to be modified.
    :type group_dn: str

    """

    dajax = Dajax()

    # Prevent a user from removing himself/herself from the group
    if account_name == request.user.username:
        dajax.alert("For security reasons, one cannot delete oneself from a group.")
        return dajax.json()

    ad_group_instance = ADGroup(group_dn)
    ad_group_instance.remove_member(account_name)

    dajax.remove("#member_" + account_name)

    return dajax.json()


@dajaxice_register
def remove_resnet_tech(request, account_name, group_dn):
    """ Removes members from both the resnet tech and resnet techadmin groups.

    :param account_name: The member's account name.
    :type account_name: str
    :param group_dn: The distinguished name of the active directory group to be modified.
    :type group_dn: str

    """

    dajax = Dajax()

    # Prevent a user from removing himself/herself from the group
    if account_name == request.user.username or account_name == request.user.username + "-admin":
        dajax.alert("For security reasons, one cannot delete oneself from a group.")
        return dajax.json()
    intern_ad_group_instance = ADGroup("CN=UH-ResTech-Users,OU=ResNet,OU=Residential Life,OU=Groups,OU=Delegated,OU=UH,OU=Depts,DC=CP-Calpoly,DC=edu")
    intern_admin_ad_group_instance = ADGroup("CN=UH-ResTech-Admins,OU=ResNet,OU=Residential Life,OU=Groups,OU=Delegated,OU=UH,OU=Depts,DC=CP-Calpoly,DC=edu")

    # Remove from SRS
    ticket = AccountRequest(subject_username=account_name)
    ticket.request_type = 'Account Modification'
    ticket.action = 'Please remove from ResNet team.'
    ticket.save()

    sr_number = ticket.ticket_id

    dajax.alert("A request to remove %(account_name)s from the ResNet team has been created. Please use SR#%(sr_number)s as a reference." % {'account_name': account_name, 'sr_number': sr_number})

    # Remove from AD
    intern_ad_group_instance.remove_member(account_name)
    intern_admin_ad_group_instance.remove_member(account_name + "-admin")

    dajax.remove("#member_" + account_name)

    return dajax.json()
