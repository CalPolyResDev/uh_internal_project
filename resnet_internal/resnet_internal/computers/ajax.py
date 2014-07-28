"""
.. module:: resnet_internal.computers.ajax
   :synopsis: ResNet Internal Computer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.conf import settings
from django.core.urlresolvers import reverse

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from srsconnector.models import PinholeRequest, DomainNameRequest

from resnet_internal.core.models import StaffMapping
from .models import Computer, Pinhole, DomainName
from .constants import (CORE, HOUSING_ADMINISTRATION, HOUSING_SERVICES, RESIDENTIAL_LIFE_AND_EDUCATION,
                        CORE_SUB_DEPARTMENTS, HOUSING_ADMINISTRATION_SUB_DEPARTMENTS, HOUSING_SERVICES_SUB_DEPARTMENTS,
                        RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS)

logger = logging.getLogger(__name__)


@dajaxice_register
def update_sub_department(request, department, sub_department_selection=None):
    """ Update sub-department drop-down choices based on the department chosen.

    :param department: The department for which to display sub-department choices.
    :type department: str

    :param sub_department_selection: The sub_department selected before form submission.
    :type sub_department_selection: str

    """

    dajax = Dajax()

    sub_department_options = {
        CORE: [(sub_department, sub_department) for sub_department in CORE_SUB_DEPARTMENTS],
        HOUSING_ADMINISTRATION: [(sub_department, sub_department) for sub_department in HOUSING_ADMINISTRATION_SUB_DEPARTMENTS],
        HOUSING_SERVICES: [(sub_department, sub_department) for sub_department in HOUSING_SERVICES_SUB_DEPARTMENTS],
        RESIDENTIAL_LIFE_AND_EDUCATION: [(sub_department, sub_department) for sub_department in RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS],
    }
    choices = []

    # Add options iff a department is selected
    if str(department) != "":
        for value, label in sub_department_options[str(department)]:
            if sub_department_selection and value == sub_department_selection:
                choices.append("<option value='%s' selected='selected'>%s</option>" % (value, label))
            else:
                choices.append("<option value='%s'>%s</option>" % (value, label))
    else:
        choices.append("<option value='%s'>%s</option>" % ("", "---------"))

    dajax.assign('#id_sub_department', 'innerHTML', ''.join(choices))

    return dajax.json()


@dajaxice_register
def modify_computer(request, request_dict, row_id, row_zero, username):
    dajax = Dajax()

    # Add a temporary loading image to the first column in the edited row
    dajax.assign("#%s:eq(0)" % row_id, 'innerHTML', '<img src="%simages/datatables/load.gif" />' % settings.STATIC_URL)

    # Update the database
    computer_instance = Computer.objects.get(id=row_id)

    for column, value in request_dict.items():
        # DN cleanup
        if column == "dn":
            dn_pieces = value.split(",")
            stripped_dn_pieces = []

            for dn_piece in dn_pieces:
                try:
                    group_type, group_string = dn_piece.split("=")
                except ValueError:
                    dajax.alert("Please enter a valid DN.")
                    dajax.script('computer_index.fnDraw();')
                    return dajax.json()

                stripped_dn_pieces.append('%(type)s=%(string)s' % {'type': group_type.strip(), 'string': group_string.strip()})

            value = ', '.join(stripped_dn_pieces)

        setattr(computer_instance, column, value)

    computer_instance.save()

    # Redraw the table
    dajax.script('computer_index.fnDraw();')

    return dajax.json()


@dajaxice_register
def remove_computer(request, computer_id):
    """ Removes computers from the computer index if no pinhole/domain name records are associated with it.

    :param computer_id: The computer's id.
    :type computer_id: str

    """

    dajax = Dajax()

    computer_instance = Computer.objects.get(id=computer_id)
    ip_address = computer_instance.ip_address

    pinholes_count = Pinhole.objects.filter(ip_address=ip_address).count()
    domain_names_count = DomainName.objects.filter(ip_address=ip_address).count()

    if pinholes_count > 0 or domain_names_count > 0:
        dajax.alert("This computer cannot be deleted because it still has pinholes and/or domain names associated with it.")
    else:
        computer_instance.delete()

    # Redraw the table
    dajax.script('computer_index.fnDraw();')

    return dajax.json()


@dajaxice_register
def remove_pinhole(request, pinhole_id):
    dajax = Dajax()

    # Get the Pinhole record
    pinhole = Pinhole.objects.get(id=int(pinhole_id))

    if request.user.is_developer:
        requestor_username = StaffMapping.objects.get(staff_title="ResNet: Assistant Resident Coordinator").staff_alias
    else:
        requestor_username = request.user.username

    ip_address = pinhole.ip_address
    inner_fw = pinhole.inner_fw
    border_fw = pinhole.border_fw
    tcp_ports = pinhole.tcp_ports
    udp_ports = pinhole.udp_ports
    submitter = request.user.get_full_name()

    description = """Please remove the following pinholes from [%(ip_address)s]:

Remove from Inner Firewall? %(inner_fw)s
Remove from Border Firewall? %(border_fw)s

------------------------TCP------------------------
%(tcp_ports)s

------------------------UDP------------------------
%(udp_ports)s

Thanks,
%(submitter)s (via ResNet Internal)""" % {'ip_address': ip_address, 'inner_fw': inner_fw, 'border_fw': border_fw, 'tcp_ports': tcp_ports, 'udp_ports': udp_ports, 'submitter': submitter}

    # Create service request
    pinhole_removal_request = PinholeRequest(priority='Low', requestor_username=requestor_username, work_log='Created Ticket for %s.' % submitter, description=description)
    pinhole_removal_request.summary = 'Pinhole Removal Request via ResNet Internal'
    pinhole_removal_request.save()

    sr_number = pinhole_removal_request.ticket_id

    # Delete the pinhole record
    pinhole.delete()

    dajax.alert("A pinhole removal request has been created in your name. Please use SR#%(sr_number)s as a reference." % {'sr_number': sr_number})

    dajax.redirect(reverse('view_uh_computer_record', kwargs={'ip_address': ip_address}))

    return dajax.json()


@dajaxice_register
def remove_domain_name(request, domain_name_id):
    dajax = Dajax()

    # Get the Domain Name record
    domain_name_record = DomainName.objects.get(id=int(domain_name_id))

    if request.user.is_developer:
        requestor_username = StaffMapping.objects.get(staff_title="ResNet: Assistant Resident Coordinator").staff_alias
    else:
        requestor_username = request.user.username

    ip_address = domain_name_record.ip_address
    domain_name = domain_name_record.domain_name
    submitter = request.user.get_full_name()

    description = """Please remove the following DNS Alias from [%(ip_address)s]:

%(domain_name)s

Thanks,
%(submitter)s (via ResNet Internal)""" % {'ip_address': ip_address, 'domain_name': domain_name, 'submitter': submitter}

    # Create service request
    domain_name_removal_request = DomainNameRequest(priority='Low', requestor_username=requestor_username, work_log='Created Ticket for %s.' % submitter, description=description)
    domain_name_removal_request.summary = 'DNS Alias Removal Request via ResNet Internal'
    domain_name_removal_request.save()

    sr_number = domain_name_removal_request.ticket_id

    # Delete the domain record
    domain_name_record.delete()

    dajax.alert("A domain name removal request has been created in your name. Please use SR#%(sr_number)s as a reference." % {'sr_number': sr_number})

    dajax.redirect(reverse('view_uh_computer_record', kwargs={'ip_address': ip_address}))

    return dajax.json()
