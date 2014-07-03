"""
.. module:: resnet_internal.computers.views
   :synopsis: ResNet Internal Computer Index Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging
import socket
import subprocess
import cStringIO as StringIO

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.servers.basehttp import FileWrapper
from django.db.models import Q
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic.edit import FormView, CreateView
from django.views.generic import TemplateView

from django_datatables_view.base_datatable_view import BaseDatatableView
from srsconnector.models import PinholeRequest, DomainNameRequest

from .forms import NewComputerForm, RequestPinholeForm, RequestDomainNameForm
from .models import Computer, Pinhole, DomainName


logger = logging.getLogger(__name__)


class ComputersView(CreateView):
    template_name = "computers/computers.html"
    form_class = NewComputerForm
    model = Computer
    fields = NewComputerForm.Meta.fields
    success_url = reverse_lazy('uh_computers')


class PopulateComputers(BaseDatatableView):
    """Renders the computer index."""

    model = Computer
    max_display_length = 250

    # define the columns that will be returned
    columns = ['id', 'department', 'sub_department', 'computer_name', 'ip_address', 'RDP', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description', 'remove']

    # define column names that can be sorted?
    order_columns = columns

    # define columns that can be searched
    searchable_columns = ['department', 'sub_department', 'computer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'dn', 'description']

    # define columns that can be edited
    editable_columns = ['department', 'sub_department', 'computer_name', 'ip_address', 'property_id', 'dn', 'description']

    def render_column(self, row, column):
        """Render columns with customized HTML.

        :param row: A dictionary containing row data.
        :type row: dict
        :param column: The name of the column to be rendered. This can be used to index into the row dictionary.
        :type column: str
        :returns: The HTML to be displayed for this column.

        """

        if column == 'ip_address':
            ip_address = getattr(row, column)

            beginning = "<div id='%s' class='editable' column='%s'><div class='display_data'><a href='/computers/%s/' class='popup_frame'>%s</a>" % (row.id, column, ip_address, ip_address)
            pinholes = "<img src='%simages/icons/pinholes.png' style='padding-left:5px;' align='top' width='16' height='16' border='0' />" % settings.STATIC_URL
            domain_names = "<img src='%simages/icons/domain_names.png' style='padding-left:5px;' align='top' width='16' height='16' border='0' />" % settings.STATIC_URL
            end = "</div><input type='text' class='editbox' value='%s' /></div>" % ip_address

            result = beginning

            # Only display the icon if the record exists
            if ip_address:
                has_pinholes = Pinhole.objects.filter(ip_address=ip_address).count() != 0
                has_domain_names = DomainName.objects.filter(ip_address=ip_address).count() != 0

                if has_pinholes:
                    result = result + pinholes
                if has_domain_names:
                    result = result + domain_names

            return result + end
        elif column == 'RDP':
            return """<div id='%s' column='%s><a href='rdp_request'><img src='%simages/icons/pinholes.png' style='padding-left:5px;' align='top' width='16' height='16' border='0' /></a>""" % (row.id, column, settings.STATIC_URL)
        elif column == 'remove':
            return """<div id='%s' column='%s'><a style="color:red; cursor:pointer;" onclick="confirm_remove(%s);">Remove</a></div>""" % (row.id, column, row.id)
        elif column in self.editable_columns:
            return "<div id='%s' class='editable' column='%s'><span class='display_data'>%s</span><input type='text' class='editbox' value='%s' /></div>" % (row.id, column, getattr(row, column), getattr(row, column))
        else:
            return "<div id='%s' column='%s'>%s</div>" % (row.id, column, getattr(row, column))

    def filter_queryset(self, qs):
        """ Filters the QuerySet by submitted search parameters.

        Made to work with multiple word search queries.
        PHP source: http://datatables.net/forums/discussion/3343/server-side-processing-and-regex-search-filter/p1
        Credit for finding the Q.AND method: http://bradmontgomery.blogspot.com/2009/06/adding-q-objects-in-django.html

        :param qs: The QuerySet to be filtered.
        :type qs: QuerySet
        :returns: If search parameters exist, the filtered QuerySet, otherwise the original QuerySet.

        """

        search_parameters = self.request.GET.get('sSearch', None)

        if search_parameters:
            params = search_parameters.split(" ")
            columnQ = None
            paramQ = None
            firstCol = True
            firstParam = True

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
                    for searchable_column in self.searchable_columns:
                        kwargz = {searchable_column + "__icontains": param}
                        q = Q(**kwargz)
                        if (firstCol):
                            firstCol = False
                            columnQ = q
                        else:
                            columnQ |= q
                    if (firstParam):
                        firstParam = False
                        paramQ = columnQ
                    else:
                        paramQ.add(columnQ, Q.AND)
                    columnQ = None
                    firstCol = True
            if paramQ:
                qs = qs.filter(paramQ)

        return qs


class ComputerRecordsView(TemplateView):
    template_name = "computers/computer_record.html"

    def get_context_data(self, **kwargs):
        context = super(ComputerRecordsView, self).get_context_data(**kwargs)

        ip_address = context['ip_address']
        error_string = "There is no dns record associated with this IP Address"

        socket_lookup = True
        subprocess_error = False

        #
        # A socket lookup on the local machine doesn't hit the DNS server.
        # This checks if the ip is that of the local machine, and forces an
        # nslookup through the terminal instead.
        #
        # NOTE: This will only work on systems with the 'nslookup' binary (Win32)
        #
        if ip_address == socket.gethostbyname(socket.gethostname()):
            socket_lookup = False

            try:
                response = subprocess.check_output(["nslookup", ip_address], stderr=subprocess.STDOUT)
                dns_record = response.split("Name:    ")[-1].split("\r\n")[0]
            except (OSError, WindowsError):
                logger.error("This server does not have the 'nslookup' binary.")
                socket_lookup = True
                subprocess_error = True

        if socket_lookup:
            try:
                dns_record = socket.gethostbyaddr(ip_address)[0]

                if subprocess_error:
                    dns_record = "%s (local hostname)" % dns_record
            except socket.herror:
                dns_record = error_string

        pinholes = Pinhole.objects.filter(ip_address=ip_address)
        domain_names = DomainName.objects.filter(ip_address=ip_address)

        context['pinholes'] = pinholes
        context['dns_record'] = dns_record
        context['domain_names'] = domain_names

        return context


class RDPRequestView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        ip_address = context["ip_address"]
        rdp_file = StringIO.StringIO()
        rdp_file.write("full address:s:" + ip_address)

        response = HttpResponse(FileWrapper(rdp_file.getValue()), content_type='application/rdp')
        response['Content-Disposition'] = 'attachment; filename=' + context["computer_name"] + '.rdp'
        return response


class PinholeRequestView(FormView):
    template_name = "computers/pinhole_request.html"
    form_class = RequestPinholeForm

    def form_valid(self, form):
        submitter = self.request.user.get_full_name()
        priority = form.cleaned_data['priority']
        requestor_username = form.cleaned_data['requestor_username']

        ip_address = self.kwargs['ip_address']
        service_name = form.cleaned_data['service_name']
        inner_fw = form.cleaned_data['inner_fw']
        border_fw = form.cleaned_data['border_fw']
        tcp_ports = "[%s]" % form.cleaned_data['tcp_ports']
        udp_ports = "[%s]" % form.cleaned_data['udp_ports']

        description = """Please add the following pinholes to [%(ip_address)s]:

Inner Firewall? %(inner_fw)s
Border Firewall? %(border_fw)s

------------------------TCP------------------------
%(tcp_ports)s

------------------------UDP------------------------
%(udp_ports)s

Thanks,
%(submitter)s (via ResNet Internal)""" % {'ip_address': ip_address, 'inner_fw': inner_fw, 'border_fw': border_fw, 'tcp_ports': tcp_ports, 'udp_ports': udp_ports, 'submitter': submitter}

        # Create service request
        new_pinhole_request = PinholeRequest(priority=priority, requestor_username=requestor_username, work_log='Created Ticket for %s.' % submitter, description=description)
        new_pinhole_request.save()

        sr_number = new_pinhole_request.ticket_id

        # Create Pinhole record
        new_pinhole = Pinhole()
        new_pinhole.ip_address = ip_address
        new_pinhole.service_name = service_name
        new_pinhole.inner_fw = bool(inner_fw)
        new_pinhole.border_fw = bool(border_fw)
        new_pinhole.tcp_ports = tcp_ports
        new_pinhole.udp_ports = udp_ports
        new_pinhole.sr_number = sr_number
        new_pinhole.save()

        return HttpResponseRedirect(reverse('view_uh_computer_record', kwargs={'ip_address': ip_address}))


class DomainNameRequestView(FormView):
    template_name = "computers/domain_name_request.html"
    form_class = RequestDomainNameForm

    def form_valid(self, form):
        submitter = self.request.user.get_full_name()
        priority = form.cleaned_data['priority']
        requestor_username = form.cleaned_data['requestor_username']

        ip_address = self.kwargs['ip_address']

        domain_names_raw = "".join(form.cleaned_data['domain_names'].split())
        domain_names_list = domain_names_raw.split(",")
        domain_names_split = domain_names_raw.replace(",", "\n")

        description = """Please add the following DNS Aliases to [%(ip_address)s]:

%(domain_names_split)s

Thanks,
%(submitter)s (via ResNet Internal)""" % {'ip_address': ip_address, 'domain_names_split': domain_names_split, 'submitter': submitter}

        # Create service request
        new_domain_name_request = DomainNameRequest(priority=priority, requestor_username=requestor_username, work_log='Created Ticket for %s.' % submitter, description=description)
        new_domain_name_request.save()

        sr_number = new_domain_name_request.ticket_id

        # Create Domain Name records
        for domain_name in domain_names_list:
            new_domain_name = DomainName()
            new_domain_name.ip_address = ip_address
            new_domain_name.domain_name = domain_name
            new_domain_name.sr_number = sr_number
            new_domain_name.save()

        return HttpResponseRedirect(reverse('view_uh_computer_record', kwargs={'ip_address': ip_address}))
