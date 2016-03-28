"""
.. module:: resnet_internal.apps.core.permissions
   :synopsis: University Housing Internal Core Permissions

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from ...settings.base import (TICKET_ACCESS, ROOMS_ACCESS, ROOMS_MODIFY_ACCESS, DAILY_DUTIES_ACCESS, TECHNICIAN_LIST_ACCESS,
                              NETWORK_ACCESS, NETWORK_MODIFY_ACCESS, COMPUTERS_RECORD_MODIFY_ACCESS, CSD_ASSIGNMENT_ACCESS,
                              ORIENTATION_ACCESS, COMPUTERS_ACCESS, PRINTERS_ACCESS, COMPUTERS_MODIFY_ACCESS, PRINTERS_MODIFY_ACCESS,
                              ROSTER_ACCESS, RESIDENT_LOOKUP_ACCESS, PRINTER_REQUEST_CREATE_ACCESS)


def permissions_check(class_name, raise_exception=True):
    """
    Decorator for views that checks whether a user has permission to view the
    requested page, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.

    :param group_list: A list of group display names that should be allowed in.
    :type group_list: list
    :param raise_exception: Determines whether or not to throw an exception when permissions test fails.
    :type raise_exception: bool

    """

    def check_perms(user):
        # First check if the user has the permission (even anon users)
        if user.has_access(class_name):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms)

ticket_access = permissions_check(TICKET_ACCESS)
rooms_access = permissions_check(ROOMS_ACCESS)
rooms_modify_access = permissions_check(ROOMS_MODIFY_ACCESS)
daily_duties_access = permissions_check(DAILY_DUTIES_ACCESS)
orientation_access = permissions_check(ORIENTATION_ACCESS)
technician_list_access = permissions_check(TECHNICIAN_LIST_ACCESS)

network_access = permissions_check(NETWORK_ACCESS)
network_modify_access = permissions_check(NETWORK_MODIFY_ACCESS)

computers_access = permissions_check(COMPUTERS_ACCESS)
computers_modify_access = permissions_check(COMPUTERS_MODIFY_ACCESS)
computer_record_modify_access = permissions_check(COMPUTERS_RECORD_MODIFY_ACCESS)

printers_access = permissions_check(PRINTERS_ACCESS)
printers_modify_access = permissions_check(PRINTERS_MODIFY_ACCESS)

csd_assignment_access = permissions_check(CSD_ASSIGNMENT_ACCESS)
roster_access = permissions_check(ROSTER_ACCESS)

resident_lookup_access = permissions_check(RESIDENT_LOOKUP_ACCESS)
printer_request_create_access = permissions_check(PRINTER_REQUEST_CREATE_ACCESS)
