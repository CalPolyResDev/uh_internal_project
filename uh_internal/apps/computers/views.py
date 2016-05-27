"""
.. module:: resnet_internal.apps.computers.views
   :synopsis: University Housing Internal Computer Index Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging
import socket
import subprocess

from clever_selects.views import ChainedSelectFormViewMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.http.response import HttpResponseRedirect, HttpResponse
from django.utils.encoding import smart_str
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from srsconnector.models import PinholeRequest, DomainNameRequest

from ..datatables.views import DatatablesView
from .ajax import PopulateComputers
from .forms import ComputerForm, RequestPinholeForm, RequestDomainNameForm
from .models import Computer, Pinhole, DomainName


logger = logging.getLogger(__name__)


class ComputersView(ChainedSelectFormViewMixin, DatatablesView):

    template_name = "computers/computers.djhtml"
    form_class = ComputerForm
    populate_class = PopulateComputers
    model = Computer
    success_url = reverse_lazy('computers:home')


class ComputerRecordsView(TemplateView):

    template_name = "computers/computer_record.djhtml"

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
                response = smart_str(subprocess.check_output(["nslookup", ip_address], stderr=subprocess.STDOUT))
                dns_record = response.split("Name:    ")[-1].split("\r\n")[0]
            except OSError:
                logger.error("This server does not have the 'nslookup' binary.", exc_info=True, extra={'request': self.request})
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

        response = HttpResponse(content_type='application/rdp')
        response['Content-Disposition'] = 'attachment; filename=' + ip_address + '.rdp'
        response.write("full address:s:" + ip_address)

        return response


class PinholeRequestView(FormView):
    template_name = "computers/pinhole_request.djhtml"
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
%(submitter)s (via University Housing Internal)""" % {'ip_address': ip_address, 'inner_fw': inner_fw, 'border_fw': border_fw, 'tcp_ports': tcp_ports, 'udp_ports': udp_ports, 'submitter': submitter}

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

        return HttpResponseRedirect(reverse('computers:view_record', kwargs={'ip_address': ip_address}))


class DomainNameRequestView(FormView):
    template_name = "computers/domain_name_request.djhtml"
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
%(submitter)s (via University Housing Internal)""" % {'ip_address': ip_address, 'domain_names_split': domain_names_split, 'submitter': submitter}

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

        return HttpResponseRedirect(reverse('computers:view_record', kwargs={'ip_address': ip_address}))
