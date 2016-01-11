"""
.. module:: resnet_internal.apps.core.templatetags
   :synopsis: University Housing Internal Core User Tests.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
"""

from django import template

from ....settings.base import technician_access_test, staff_access_test, ports_access_test, ports_modify_access_test, computers_access_test, computers_modify_access_test, computer_record_modify_access_test, printers_access_test, printers_modify_access_test, developer_access_test


register = template.Library()


@register.filter
def technician_access(user):
    """ Tests if a User has technician permissions.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return technician_access_test(user)


@register.filter
def staff_access(user):
    """ Tests if a User has staff permissions.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return staff_access_test(user)


@register.filter
def developer_access(user):
    """ Tests if a User has developer permissions.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return developer_access_test(user)


@register.filter
def ports_access(user):
    """ Tests if a User has permission to view ports.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return ports_access_test(user)


@register.filter
def ports_modify_access(user):
    """ Tests if a User has permission to modify ports.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return ports_modify_access_test(user)


@register.filter
def computers_access(user):
    """ Tests if a User has permission to view computers and computer records.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return computers_access_test(user)


@register.filter
def computers_modify_access(user):
    """ Tests if a User has permission to modify computers.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return computers_modify_access_test(user)


@register.filter
def computer_record_modify_access(user):
    """ Tests if a User has permission to modify computers.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return computer_record_modify_access_test(user)


@register.filter
def printers_access(user):
    """ Tests if a User has permission to view printers and printer requests.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return printers_access_test(user)


@register.filter
def printers_modify_access(user):
    """ Tests if a User has permission to modify printers and printer requests.

    :param user: The user to test.
    :type user: InternalUser
    :returns: True if the user has the required permissions, else false.

    """

    return printers_modify_access_test(user)
