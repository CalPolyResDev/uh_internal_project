"""
.. module:: resnet_internal.computers.ajax
   :synopsis: ResNet Internal Computer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging
from collections import OrderedDict

from django.db.models import Q
from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax
from srsconnector.models import PinholeRequest, DomainNameRequest

from resnet_internal.core.models import StaffMapping
from resnet_internal.settings.base import computers_modify_access_test
from resnet_internal.datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView
from .models import Computer, Pinhole, DomainName
from .constants import (CORE, HOUSING_ADMINISTRATION, HOUSING_SERVICES, RESIDENTIAL_LIFE_AND_EDUCATION,
                        CORE_SUB_DEPARTMENTS, HOUSING_ADMINISTRATION_SUB_DEPARTMENTS, HOUSING_SERVICES_SUB_DEPARTMENTS,
                        RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS)
from .forms import ComputerUpdateForm

logger = logging.getLogger(__name__)


@ajax
@require_POST
def update_sub_department(request):
    """ Update sub-department drop-down choices based on the department chosen.

    :param department: The department for which to display sub-department choices.
    :type department: str

    :param sub_department_selection: The sub_department selected before form submission.
    :type sub_department_selection: str

    """

    # Pull post parameters
    department = request.POST.get("department", None)
    sub_department_selection = request.POST.get("sub_department_selection", None)

    sub_department_options = {
        CORE: [(sub_department, sub_department) for sub_department in CORE_SUB_DEPARTMENTS],
        HOUSING_ADMINISTRATION: [(sub_department, sub_department) for sub_department in HOUSING_ADMINISTRATION_SUB_DEPARTMENTS],
        HOUSING_SERVICES: [(sub_department, sub_department) for sub_department in HOUSING_SERVICES_SUB_DEPARTMENTS],
        RESIDENTIAL_LIFE_AND_EDUCATION: [(sub_department, sub_department) for sub_department in RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS],
    }
    choices = []

    # Add options iff a department is selected
    if department:
        for value, label in sub_department_options[str(department)]:
            if sub_department_selection and value == sub_department_selection:
                choices.append("<option value='%s' selected='selected'>%s</option>" % (value, label))
            else:
                choices.append("<option value='%s'>%s</option>" % (value, label))
    else:
        logger.warning("A department wasn't passed via POST.")
        choices.append("<option value='%s'>%s</option>" % ("", "---------"))

    data = {
        'inner-fragments': {
            '#id_sub_department': ''.join(choices)
        },
    }

    return data


class PopulateComputers(RNINDatatablesPopulateView):
    """Renders the computer index."""

    table_name = "computer_index"
    data_source = reverse_lazy('populate_uh_computers')
    update_source = reverse_lazy('update_uh_computer')
    model = Computer

    # NOTE Installed Types: ip-address, mac-address

    column_definitions = OrderedDict()
    column_definitions["id"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "ID"}
    column_definitions["department"] = {"width": "225px", "type": "string", "title": "Department"}
    column_definitions["sub_department"] = {"width": "225px", "type": "string", "title": "Sub Department"}
    column_definitions["computer_name"] = {"width": "150px", "type": "string", "title": "Computer Name"}
    column_definitions["mac_address"] = {"width": "150px", "type": "mac-address", "editable": False, "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "ip-address", "title": "IP Address"}
    column_definitions["RDP"] = {"width": "50px", "type": "html", "searchable": False, "orderable": False, "editable": False, "title": "RDP"}
    column_definitions["model"] = {"width": "100px", "type": "string", "editable": False, "title": "Model"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "editable": False, "title": "Serial Number"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["dn"] = {"width": "225px", "type": "string", "title": "Distinguished Name"}
    column_definitions["description"] = {"width": "225px", "type": "string", "className": "edit_trigger", "title": "Description"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "search": "Filter records: (Use ?pinhole and/or ?domain to narrow results.)",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"] = {"width": "50px", "type": "string", "searchable": False, "orderable": False, "editable": False, "title": "&nbsp;"}

        return super(PopulateComputers, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = computers_modify_access_test(user)

    def render_column(self, row, column):

        if column == 'ip_address':
            value = getattr(row, column)

            try:
                record_url = reverse('view_uh_computer_record', kwargs={'ip_address': row.ip_address})
            except NoReverseMatch:
                editable_block = self.editable_block_template.format(value=value)
                return self.base_column_template.format(id=row.id, class_name="editable", column=column, value=value, link_block="", inline_images="", editable_block=editable_block)
            else:
                editable_block = self.editable_block_template.format(value=value)
                link_block = self.link_block_template.format(link_url=record_url, onclick_action="", link_target="", link_class_name="popup_frame", link_style="", link_text=value)

                pinholes = self.icon_template.format(icon_url=static('images/icons/pinholes.png'))
                domain_names = self.icon_template.format(icon_url=static('images/icons/domain_names.png'))
                inline_images = ""

                if value:
                    has_pinholes = Pinhole.objects.filter(ip_address=value).count() != 0
                    has_domain_names = DomainName.objects.filter(ip_address=value).count() != 0

                    if has_pinholes:
                        inline_images = pinholes
                    if has_domain_names:
                        inline_images = inline_images + domain_names

                return self.base_column_template.format(id=row.id, class_name="editable", column=column, value="", link_block=link_block, inline_images=inline_images, editable_block=editable_block)
        elif column == 'RDP':
            try:
                rdp_file_url = reverse('rdp_request', kwargs={'ip_address': row.ip_address})
            except NoReverseMatch:
                return self.base_column_template.format(id=row.id, class_name="", column=column, value="", link_block="", inline_images="", editable_block="")
            else:
                rdp_icon = self.icon_template.format(icon_url=static('images/icons/rdp.png'))
                link_block = self.link_block_template.format(link_url=rdp_file_url, onclick_action="", link_target="", link_class_name="", link_style="", link_text=rdp_icon)
                return self.base_column_template.format(id=row.id, class_name="", column=column, value="", link_block=link_block, inline_images="", editable_block="")
        elif column == 'remove':
            onclick = "confirm_remove({id});return false;".format(id=row.id)
            link_block = self.link_block_template.format(link_url="", onclick_action=onclick, link_target="", link_class_name="", link_style="color:red; cursor:pointer;", link_text="Remove")

            return self.base_column_template.format(id=row.id, class_name="", column=column, value="", link_block=link_block, inline_images="", editable_block="")
        else:
            return super(PopulateComputers, self).render_column(row, column)

    def filter_queryset(self, qs):
        search_parameters = self.request.GET.get('search[value]', None)
        searchable_columns = self.get_searchable_columns()

        if search_parameters:
            params = search_parameters.split(" ")
            columnQ = Q()
            paramQ = Q()

            # Check for pinhole / domain flags
            for param in params:
                if param[:1] == '?':
                    flag = param[1:]

                    if flag == "pinhole":
                        pinhole_ip_list = Pinhole.objects.values_list('ip_address', flat=True).distinct()
                        qs = qs.filter(ip_address__in=pinhole_ip_list)
                    elif flag == "domain":
                        domain_name_ip_list = DomainName.objects.values_list('ip_address', flat=True).distinct()
                        qs = qs.filter(ip_address__in=domain_name_ip_list)

            for param in params:
                if param != "" and not (param == "?pinhole" or param == "?domain"):
                    for searchable_column in searchable_columns:
                        columnQ |= Q(**{searchable_column + "__icontains": param})

                    paramQ.add(columnQ, Q.AND)
                    columnQ = Q()
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class UpdateComputer(BaseDatatablesUpdateView):
    form_class = ComputerUpdateForm
    model = Computer
    populate_class = PopulateComputers


@ajax
@require_POST
def remove_computer(request):
    """ Removes computers from the computer index if no pinhole/domain name records are associated with it.

    :param computer_id: The computer's id.
    :type computer_id: int

    """

    # Pull post parameters
    computer_id = request.POST["computer_id"]

    context = {}
    context["success"] = True
    context["error_message"] = None
    context["computer_id"] = computer_id

    computer_instance = Computer.objects.get(id=computer_id)
    ip_address = computer_instance.ip_address

    pinholes_count = Pinhole.objects.filter(ip_address=ip_address).count()
    domain_names_count = DomainName.objects.filter(ip_address=ip_address).count()

    if pinholes_count > 0 or domain_names_count > 0:
        context["success"] = False
        context["error_message"] = "This computer cannot be deleted because it still has pinholes and/or domain names associated with it."
    else:
        computer_instance.delete()

    return context


@ajax
@require_POST
def remove_pinhole(request):
    """ Removes a pinhole.

    :param pinhole_id: The pinhole's id.
    :type pinhole_id: int

    """

    # Pull post parameters
    pinhole_id = request.POST["pinhole_id"]

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

    context = {}
    context["sr_number"] = sr_number

    return context


@ajax
@require_POST
def remove_domain_name(request):
    """ Removes a domain name.

    :param domain_name_id: The domain_name's id.
    :type domain_name_id: int

    """

    # Pull post parameters
    domain_name_id = request.POST["domain_name_id"]

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

    context = {}
    context["sr_number"] = sr_number

    return context
