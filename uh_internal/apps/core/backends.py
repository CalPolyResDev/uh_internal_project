"""
.. module:: resnet_internal.apps.core.backends
   :synopsis: University Housing Internal Core Authentication Backends.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import logging

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django_cas_ng.backends import CASBackend
from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader
from ldap_groups.exceptions import InvalidGroupDN
from ldap_groups.utils import escape_query
from ldap_groups.groups import ADGroup as LDAPADGroup

from .models import ADGroup


logger = logging.getLogger(__name__)


class CASLDAPBackend(CASBackend):
    """CAS authentication backend with LDAP attribute retrieval."""

    def authenticate(self, request, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""

        user = super(CASLDAPBackend, self).authenticate(request, ticket, service)

        # Populate user attributes
        if user:
            try:
                server = Server(settings.LDAP_GROUPS_SERVER_URI)
                connection = Connection(server=server,
                                        auto_bind=True,
                                        user=settings.LDAP_GROUPS_BIND_DN,
                                        password=settings.LDAP_GROUPS_BIND_PASSWORD,
                                        raise_exceptions=True)
                connection.start_tls()

                account_def = ObjectDef('user')
                account_def += AttrDef('userPrincipalName')
                account_def += AttrDef('displayName')
                account_def += AttrDef('givenName')
                account_def += AttrDef('sn')
                account_def += AttrDef('mail')

                account_reader = Reader(connection=connection,
                                        object_def=account_def,
                                        query="userPrincipalName: {principal_name}".format(principal_name=user.username),
                                        base=settings.LDAP_GROUPS_BASE_DN)
                account_reader.search_subtree()

                user_info = account_reader.entries[0]
            except Exception as msg:
                logger.exception(msg, exc_info=True, extra={'request': request})
            else:
                principal_name = str(user_info["userPrincipalName"])
                username = principal_name.split("@")[0]

                user_group_objects = Reader(connection=connection,
                                            object_def=account_def,
                                            query='(&(member=CN={username},OU=People,OU=Enterprise,OU=Accounts,DC=ad,DC=calpoly,DC=edu)(objectClass=group))'.format(username=username),
                                            base=settings.LDAP_GROUPS_BASE_DN).search()

                user_groups = []
                for group in user_group_objects:
                    user_groups.append(group.entry_dn)

                def AD_get_children(connection, parent):
                    connection.search(settings.LDAP_GROUPS_BASE_DN,
                                      "(&(objectCategory=group)(memberOf={group_name}))".format(group_name=escape_query(parent)))
                    children = connection.entries
                    results = []
                    for child in children:
                        results.append(child.entry_dn)
                    return results

                def get_descendants(connection, parent):
                    descendants = []
                    queue = []
                    queue.append(parent)
                    visited = set()

                    while len(queue):
                        node = queue.pop()

                        if node not in visited:
                            children = AD_get_children(connection, node)
                            for child in children:
                                if child not in descendants:
                                    descendants.append(child)
                                    queue.append(child)
                            visited.add(node)

                    return descendants

                # New Code should use the ad_groups property of the user to enforce permissions
                user.ad_groups.clear()

                for group_id, group_dn in ADGroup.objects.all().values_list('id', 'distinguished_name'):
                    if group_dn in user_groups:
                        user.ad_groups.add(group_id)
                    else:
                        children = get_descendants(connection, group_dn)
                        for child in children:
                            if child in user_groups:
                                user.ad_groups.add(group_id)

                if not user.ad_groups.exists():
                    raise PermissionDenied('User %s is not in any of the allowed groups.' % principal_name)

                if not user.ad_groups.all().filter(distinguished_name='CN=UH-RN-DevTeam,OU=Technology,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu').exists() and settings.RESTRICT_LOGIN_TO_DEVELOPERS:
                    raise PermissionDenied('Only developers can access the site on this server. Please use the primary site.')

                def get_group_members(group):
                    cache_key = 'group_members::' + (group if " " not in group else group.replace(" ", "_"))
                    group_members = cache.get(cache_key)

                    if group_members is None:
                        try:
                            group_members = LDAPADGroup(group).get_tree_members()
                        except InvalidGroupDN:
                            logger.exception('Could not retrieve group members for DN: ' + group,
                                             exc_info=True,
                                             extra={'request': request})
                            return []

                        group_members = [member["userPrincipalName"] for member in group_members]
                        cache.set(cache_key, group_members, 60)

                    return group_members

                # Django Flags
                developer_list = get_group_members('CN=UH-RN-DevTeam,OU=Technology,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu')
                user.is_developer = principal_name in developer_list
                user.is_staff = principal_name in developer_list
                user.is_superuser = principal_name in developer_list

                user.full_name = user_info["displayName"]
                user.first_name = user_info["givenName"]
                user.last_name = user_info["sn"]
                user.email = user_info["mail"]

                user.save()

        return user
