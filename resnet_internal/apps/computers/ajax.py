"""
.. module:: resnet_internal.apps.computers.ajax
   :synopsis: University Housing Internal Computer Index AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from collections import OrderedDict
from datetime import datetime
import logging
import shlex

from dateutil.relativedelta import relativedelta
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.db.models import Q
from django.views.decorators.http import require_POST
from django_ajax.decorators import ajax
from srsconnector.models import PinholeRequest, DomainNameRequest

from ...settings.base import COMPUTERS_MODIFY_ACCESS
from ..core.models import StaffMapping
from ..datatables.ajax import RNINDatatablesPopulateView, BaseDatatablesUpdateView, BaseDatatablesRemoveView, RNINDatatablesFormView
from .forms import ComputerForm
from .models import Computer, Pinhole, DomainName


logger = logging.getLogger(__name__)

OLD_YEARS = 3
OLDER_YEARS = 4
REPLACE_YEARS = 5


class PopulateComputers(RNINDatatablesPopulateView):
    """Renders the computer index."""

    table_name = "computer_index"

    data_source = reverse_lazy('populate_computers')
    update_source = reverse_lazy('update_computer')
    form_source = reverse_lazy('form_computer')

    form_class = ComputerForm
    model = Computer

    item_name = 'computer'
    remove_url_name = 'remove_computer'

    column_definitions = OrderedDict()
    column_definitions["department"] = {"width": "200px", "type": "string", "title": "Department", "related": True, "lookup_field": "name"}
    column_definitions["sub_department"] = {"width": "200px", "type": "string", "title": "Sub Department", "related": True, "lookup_field": "name"}
    column_definitions["display_name"] = {"width": "200px", "type": "string", "title": "Computer Name"}
    column_definitions["mac_address"] = {"width": "150px", "type": "string", "title": "MAC Address"}
    column_definitions["ip_address"] = {"width": "150px", "type": "string", "title": "IP Address"}
    column_definitions["RDP"] = {"width": "50px", "type": "html", "searchable": False, "orderable": False, "editable": False, "title": "RDP"}
    column_definitions["model"] = {"width": "200px", "type": "string", "title": "Model"}
    column_definitions["serial_number"] = {"width": "100px", "type": "string", "title": "Serial Number"}
    column_definitions["property_id"] = {"width": "100px", "type": "string", "title": "Property ID"}
    column_definitions["location"] = {"width": "150px", "type": "string", "title": "Location"}
    column_definitions["date_purchased"] = {"width": "100px", "type": "string", "searchable": False, "title": "Date Purchased"}
    column_definitions["dn"] = {"width": "250px", "type": "string", "title": "Distinguished Name"}
    column_definitions["description"] = {"width": "250px", "type": "string", "title": "Description"}
    column_definitions["remove"] = {"width": "0px", "searchable": False, "orderable": False, "visible": False, "editable": False, "title": "&nbsp;"}

    extra_options = {
        "language": {
            "search": "Filter records: (?pinhole, ?domain, ?dhcp, ?replace) ",
        },
    }

    def get_options(self):
        if self.get_write_permissions():
            self.column_definitions["remove"].update({"width": "80px", "type": "string", "remove_column": True, "visible": True})

        return super(PopulateComputers, self).get_options()

    def _initialize_write_permissions(self, user):
        self.write_permissions = user.has_access(COMPUTERS_MODIFY_ACCESS)

    def get_row_class(self, row):
        if row.date_purchased:
            old_delta = datetime.now() - relativedelta(years=OLD_YEARS)
            older_delta = datetime.now() - relativedelta(years=OLDER_YEARS)
            replace_delta = datetime.now() - relativedelta(years=REPLACE_YEARS)

            puchase_datetime = datetime.fromordinal(row.date_purchased.toordinal())

            if puchase_datetime <= replace_delta:
                return "replace"
            elif puchase_datetime <= older_delta and puchase_datetime > replace_delta:
                return "older"
            elif puchase_datetime <= old_delta and puchase_datetime > older_delta:
                return "old"

    def get_display_block(self, row, column):
        if column == 'ip_address':
            raw_display_value = self.get_raw_value(row, column)
            display_value = raw_display_value if raw_display_value else "DHCP"

            # Add the record link block
            link_block = ""
            inline_images = ""

            try:
                record_url = reverse('view_computer_record', kwargs={'ip_address': getattr(row, column)})
            except NoReverseMatch:
                pass
            else:
                # Don't duplicate display value
                display_value = ""

                onclick = """openModalFrame("Association Record for {ip_address}", "{url}");""".format(ip_address=raw_display_value, url=record_url)
                link_block = self.onclick_link_block_template.format(onclick_action=onclick, link_class_name="", link_display=raw_display_value)

                # Add pinhole/domain name icons
                pinholes = self.icon_template.format(icon_url=static('images/icons/pinholes.png'))
                domain_names = self.icon_template.format(icon_url=static('images/icons/domain_names.png'))

                has_pinholes = Pinhole.objects.filter(ip_address=raw_display_value).exists()
                has_domain_names = DomainName.objects.filter(ip_address=raw_display_value).exists()

                if has_pinholes:
                    inline_images = pinholes
                if has_domain_names:
                    inline_images += domain_names

            return self.display_block_template.format(value=display_value, link_block=link_block, inline_images=inline_images)
        else:
            return super(PopulateComputers, self).get_display_block(row, column)

    def render_column(self, row, column):
        if column == 'RDP':
            try:
                rdp_file_url = reverse('rdp_request', kwargs={'ip_address': row.ip_address})
            except NoReverseMatch:
                link_block = ""
            else:
                rdp_icon = self.icon_template.format(icon_url=static('images/icons/rdp.png'))
                link_block = self.href_link_block_template.format(link_url=rdp_file_url, link_class_name="", link_display=rdp_icon)

            display_block = self.display_block_template.format(value="", link_block=link_block, inline_images="")
            return self.base_column_template.format(column=column, display_block=display_block, form_field_block="")
        else:
            return super(PopulateComputers, self).render_column(row, column)

    def filter_queryset(self, qs):
        search_parameters = self.request.GET.get('search[value]', None)
        searchable_columns = self.get_searchable_columns()
        flags = ["?pinhole", "?domain", "?dhcp", "?old", "?older", "?replace"]

        if search_parameters:
            try:
                params = shlex.split(search_parameters)
            except ValueError:
                params = search_parameters.split(" ")
            columnQ = Q()
            paramQ = Q()

            # Check for flags
            for param in params:
                if param[:1] == '?':
                    flag = param[1:]

                    if flag == "pinhole":
                        pinhole_ip_list = Pinhole.objects.values_list('ip_address', flat=True).distinct()
                        qs = qs.filter(ip_address__in=pinhole_ip_list)
                    elif flag == "domain":
                        domain_name_ip_list = DomainName.objects.values_list('ip_address', flat=True).distinct()
                        qs = qs.filter(ip_address__in=domain_name_ip_list)
                    elif flag == "dhcp":
                        qs = qs.filter(dhcp=True)
                    elif flag == "old":
                        qs = qs.filter(date_purchased__lte=datetime.now() - relativedelta(years=OLD_YEARS))
                    elif flag == "older":
                        qs = qs.filter(date_purchased__lte=datetime.now() - relativedelta(years=OLDER_YEARS))
                    elif flag == "replace":
                        qs = qs.filter(date_purchased__lte=datetime.now() - relativedelta(years=REPLACE_YEARS))

            for param in params:
                if param != "" and param not in flags:
                    for searchable_column in searchable_columns:
                        columnQ |= Q(**{searchable_column + "__icontains": param})

                    paramQ.add(columnQ, Q.AND)
                    columnQ = Q()
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class RetrieveComputerForm(RNINDatatablesFormView):
    populate_class = PopulateComputers


class UpdateComputer(BaseDatatablesUpdateView):
    form_class = ComputerForm
    model = Computer
    populate_class = PopulateComputers


class RemoveComputer(BaseDatatablesRemoveView):
    model = Computer

    def post(self, request, *args, **kwargs):
        """ Removes computers from the computer index if no pinhole/domain name records are associated with it.

        :param computer_id: The computer's id.
        :type computer_id: int

        """

        # Pull post parameters
        computer_id = request.POST["item_id"]

        response = {}
        response["success"] = True
        response["error_message"] = None
        response["item_id"] = computer_id

        computer_instance = Computer.objects.get(id=computer_id)
        ip_address = computer_instance.ip_address

        pinholes_count = Pinhole.objects.filter(ip_address=ip_address).count()
        domain_names_count = DomainName.objects.filter(ip_address=ip_address).count()

        if pinholes_count > 0 or domain_names_count > 0:
            response["success"] = False
            response["error_message"] = "This computer cannot be deleted because it still has pinholes and/or domain names associated with it."
        else:
            computer_instance.delete()

        return response


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
        requestor_username = StaffMapping.objects.get(title="ResNet: Assistant Resident Coordinator").email
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
%(submitter)s (via University Housing Internal)""" % {'ip_address': ip_address, 'inner_fw': inner_fw, 'border_fw': border_fw, 'tcp_ports': tcp_ports, 'udp_ports': udp_ports, 'submitter': submitter}

    # Create service request
    pinhole_removal_request = PinholeRequest(priority='Low', requestor_username=requestor_username, work_log='Created Ticket for %s.' % submitter, description=description)
    pinhole_removal_request.summary = 'Pinhole Removal Request via University Housing Internal'
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
        requestor_username = StaffMapping.objects.get(title="ResNet: Assistant Resident Coordinator").email
    else:
        requestor_username = request.user.username

    ip_address = domain_name_record.ip_address
    domain_name = domain_name_record.domain_name
    submitter = request.user.get_full_name()

    description = """Please remove the following DNS Alias from [%(ip_address)s]:

%(domain_name)s

Thanks,
%(submitter)s (via University Housing Internal)""" % {'ip_address': ip_address, 'domain_name': domain_name, 'submitter': submitter}

    # Create service request
    domain_name_removal_request = DomainNameRequest(priority='Low', requestor_username=requestor_username, work_log='Created Ticket for %s.' % submitter, description=description)
    domain_name_removal_request.summary = 'DNS Alias Removal Request via University Housing Internal'
    domain_name_removal_request.save()

    sr_number = domain_name_removal_request.ticket_id

    # Delete the domain record
    domain_name_record.delete()

    context = {}
    context["sr_number"] = sr_number

    return context
