"""
.. module:: resnet_internal.apps.core.backends
   :synopsis: University Housing Internal Core Authentication Backends.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from concurrent.futures.thread import ThreadPoolExecutor
import logging

from django.conf import settings
from django.core.cache import cache
from django_cas_ng.backends import CASBackend
from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader
from ldap_groups.exceptions import InvalidGroupDN
from ldap_groups.groups import ADGroup as LDAPADGroup

from ..core.models import ADGroup


logger = logging.getLogger(__name__)


class CASLDAPBackend(CASBackend):
    """CAS authentication backend with LDAP attribute retrieval."""

    def authenticate(self, ticket, service, request):
        """Verifies CAS ticket and gets or creates User object"""

        user = super(CASLDAPBackend, self).authenticate(ticket, service, request)

        # Populate user attributes
        if user:
            try:
                server = Server(settings.LDAP_GROUPS_SERVER_URI)
                connection = Connection(server=server, auto_bind=True, user=settings.LDAP_GROUPS_BIND_DN, password=settings.LDAP_GROUPS_BIND_PASSWORD, raise_exceptions=True)
                connection.start_tls()

                account_def = ObjectDef('user')
                account_def.add(AttrDef('userPrincipalName'))
                account_def.add(AttrDef('displayName'))
                account_def.add(AttrDef('givenName'))
                account_def.add(AttrDef('sn'))
                account_def.add(AttrDef('mail'))

                account_reader = Reader(connection=connection, object_def=account_def, query="userPrincipalName: {principal_name}".format(principal_name=user.username), base=settings.LDAP_GROUPS_BASE_DN)
                account_reader.search_subtree()

                user_info = account_reader.entries[0]
            except Exception as msg:
                logger.exception(msg)
            else:
                principal_name = str(user_info["userPrincipalName"])

                def get_group_members(group):
                    cache_key = 'group_members::' + group
                    group_members = cache.get(cache_key)

                    if group_members is None:
                        try:
                            group_members = LDAPADGroup(group).get_tree_members()
                        except InvalidGroupDN:
                            logger.exception('Could not retrieve group members for DN: ' + group)
                            return []

                        group_members = [member["userPrincipalName"] for member in group_members]
                        cache.set(cache_key, group_members, 60)

                    return group_members

                def check_group_for_user(group):
                    group_members = get_group_members(group.distinguished_name)
                    if principal_name in group_members:
                        user.ad_groups.add(group)

                # New Code should use the ad_groups property of the user to enforce permissions
                user.ad_groups.clear()
                with ThreadPoolExecutor(ADGroup.objects.count()) as pool:
                    pool.map(check_group_for_user, ADGroup.objects.all())

                if not user.ad_groups.exists():
                    raise PermissionError('User %s is not in any of the allowed groups.' % principal_name)

                if not user.ad_groups.all().filter(distinguished_name='CN=UH-RN-DevTeam,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu').exists() and settings.RESTRICT_LOGIN_TO_DEVELOPERS:
                    raise PermissionError('Only developers can access the site on this server. Please use the primary site.')

                # Legacy Permissions Flags
                net_admin_list = get_group_members('CN=StateHRDept - IS-ITS-Networks (132900 FacStf Only),OU=FacStaff,OU=StateHRDept,OU=Automated,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                telecom_list = get_group_members('CN=StateHRDept - IS-ITS-Telecommunications (133100 FacStf Only),OU=FacStaff,OU=StateHRDept,OU=Automated,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                tag_list = get_group_members('CN=UH-TAG,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                tag_readonly_list = get_group_members('CN=UH-TAG-READONLY,OU=User Groups,OU=Websites,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                technician_list = get_group_members('CN=UH-RN-Techs,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                rn_staff_list = get_group_members('CN=UH-RN-Staff,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                developer_list = get_group_members('CN=UH-RN-DevTeam,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')

                csd_list = get_group_members('CN=UH-CSD,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                ral_list = get_group_members('CN=UH-RAL,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                ral_manager_list = get_group_members('CN=UH-RAL-Managers,OU=User Groups,OU=Websites,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                ra_list = get_group_members('CN=UH-RA,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                fd_staff_list = get_group_members('CN=UH-FD-Staff,OU=Front Desk,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')

                user.is_net_admin = principal_name in net_admin_list
                user.is_telecom = principal_name in telecom_list
                user.is_tag = principal_name in tag_list
                user.is_tag_readonly = principal_name in tag_readonly_list
                user.is_technician = principal_name in technician_list
                user.is_rn_staff = principal_name in rn_staff_list

                user.is_developer = principal_name in developer_list
                user.is_staff = principal_name in developer_list
                user.is_superuser = principal_name in developer_list

                user.is_csd = principal_name in csd_list
                user.is_ral = principal_name in ral_list
                user.is_ral_manager = principal_name in ral_manager_list
                user.is_ra = principal_name in ra_list
                user.is_fd_staff = principal_name in fd_staff_list

                user.full_name = user_info["displayName"]
                user.first_name = user_info["givenName"]
                user.last_name = user_info["sn"]
                user.email = user_info["mail"]
                user.save()

        return user
