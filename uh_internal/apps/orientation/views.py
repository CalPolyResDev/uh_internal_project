"""
.. module:: resnet_internal.apps.orientation.views
   :synopsis: University Housing Internal Orientation Views.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from ..core.models import StaffMapping
from .forms import SRSUploadForm, OnityEmailForm


class ChecklistView(TemplateView):
    template_name = "orientation/checklist.djhtml"


class OnityDoorAccessView(FormView):
    """Orientation Checklist Item: Onity Door Access."""

    template_name = "orientation/onity_door_access.djhtml"
    form_class = OnityEmailForm
    success_url = reverse_lazy('orientation:home')

    def get_initial(self):
        full_name = self.request.user.get_full_name()
        first_name = self.request.user.first_name
        initial_message = "To Whom It May Concern:\n\nMy name is %s. I've just been hired as a ResNet technician and would like to set up an appointment to get my PolyCard coded for Onity Door Access to the ResNet offices.\n\nSincerely,\n%s" % (full_name, first_name)

        return {'message': initial_message}

    def get_context_data(self, **kwargs):
        context = super(OnityDoorAccessView, self).get_context_data(**kwargs)

        onity_staff = StaffMapping.objects.get(title="Housing: Information Technology Consultant")

        context['onity_staff_name'] = onity_staff.name
        context['onity_staff_email'] = onity_staff.email
        context['onity_staff_extension'] = onity_staff.extension

        return context

    def form_valid(self, form):
        send_mail(subject="New ResNet Technician Onity Door Access Appointment",
                  message=form.cleaned_data.get('message'),
                  from_email=self.request.user.email,
                  recipient_list=[self.request.POST['to_email']], fail_silently=False)

        return super(OnityDoorAccessView, self).form_valid(form)


class SRSAccessView(FormView):
    """Orientation Checklist Item: SRS Access."""

    template_name = "orientation/srs_access.djhtml"
    form_class = SRSUploadForm
    success_url = reverse_lazy('orientation:home')

    def form_valid(self, form):
        # Create a new account request
        from srsconnector.models import AccountRequest
        # TODO: Update to use updated srsconnector
        ticket = AccountRequest(subject_username=self.request.user.get_alias())
        ticket.save()

        return super(SRSAccessView, self).form_valid(form)


class PayrollView(TemplateView):
    template_name = "orientation/payroll_access.djhtml"
