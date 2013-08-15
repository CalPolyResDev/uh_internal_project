from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import View
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
#from resnet_internal.main.models import StaffMapping
from forms import SRSUploadForm, OnityEmailForm
from django.http.response import HttpResponseRedirect
from django.conf import settings
from srsconnector.settings import ALIAS as SRS_ALIAS
from srsconnector.models import AccountRequest
from srsconnector.ewiz.attacher import EwizAttacher

#
# Resnet Internal Orientation views
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

#
# Permissions Test
#
def orientation_test(user):
    if user.is_authenticated and (user.is_developer or user.is_new_tech):
        return True
    return False

#
# Orientation Checklist
#
class ChecklistView(View):
    template_name = 'orientation/checklist.html'

    def __render(self):
        self.request.session.set_test_cookie()
        return render_to_response(self.template_name, context_instance=RequestContext(self.request))

    @method_decorator(user_passes_test(orientation_test))
    def dispatch(self, *args, **kwargs):
        return super(ChecklistView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.__render()

#
# Orientation Checklist Item: Onity Door Access
#
# class OnityDoorAccessView(View):
#     template_name = "orientation/onityDoorAccess.html"
#     form = None
#     data = None
# 
#     def __render(self):
#         self.request.session.set_test_cookie()
#         onityStaff = StaffMapping.objects.get(staff_title="Housing: Information Technology Consultant")
#         self.data = {'onityStaffName': onityStaff.staff_name, 'onityStaffEmail': onityStaff.staff_alias + u'@calpoly.edu', 'onityStaffExt': onityStaff.staff_ext}
# 
#         return render_to_response(self.template_name, {"form": self.form, "data": self.data}, context_instance=RequestContext(self.request))
# 
#     @method_decorator(user_passes_test(orientation_test))
#     def dispatch(self, *args, **kwargs):
#         return super(OnityDoorAccessView, self).dispatch(*args, **kwargs)
# 
#     def post(self, *args, **kwargs):
#         self.form = OnityEmailForm(data=self.request.POST)
# 
#         if self.form.is_valid():
#             send_mail(subject="New ResNet Technician Onity Door Access Appointment", message=self.form.cleaned_data.get('message'), from_email=self.request.user.email, recipient_list=["alex.kavanaugh@outlook.com"], fail_silently=False)
#             return HttpResponseRedirect(reverse('orientation-checklist'))
# 
#         if self.request.session.test_cookie_worked():
#             self.request.session.delete_test_cookie()
#         return self.__render()
# 
#     def get(self, *args, **kwargs):
#         fullName = self.request.user.get_full_name()
#         firstName = self.request.user.first_name
#         initialMessage = "To Whom It May Concern:\n\nMy name is " + fullName + ". I've just been hired as a ResNet technician and would like to set up an appointment to get my PolyCard coded for Onity Door Access to the ResNet offices.\n\nSincerely,\n" + firstName
#         self.form = OnityEmailForm(initial={'message': initialMessage})
#         return self.__render()

#
# Orientation Checklist Item: SRS Access
#
class SRSAccessView(View):
    template_name = "orientation/srsAccess.html"
    form = None

    def __render(self):
        self.request.session.set_test_cookie()
        return render_to_response(self.template_name, {"form": self.form}, context_instance=RequestContext(self.request))

    @method_decorator(user_passes_test(orientation_test))
    def dispatch(self, *args, **kwargs):
        return super(SRSAccessView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.form = SRSUploadForm(self.request.POST, self.request.FILES)

        if self.form.is_valid():
            # Create a new account request
            ticket = AccountRequest(subjectUsername=self.request.user.get_alias())
            ticket.save()

            # Grab the RUP
            filePointer = self.request.FILES['signed_rup'].file

            # Upload the RUP
            EwizAttacher(settingsDict=settings.DATABASES[SRS_ALIAS], model=ticket, filePointer=filePointer, fileName=self.request.user.get_alias() + u'.pdf').attachFile()

            return HttpResponseRedirect(reverse('orientation-checklist'))

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return self.__render()

    def get(self, *args, **kwargs):
        self.form = SRSUploadForm()
        return self.__render()

#
# Orientation Checklist Item: Payroll Access
#
class PayrollAccessView(View):
    template_name = "orientation/payrollAccess.html"

    def __render(self):
        self.request.session.set_test_cookie()
        return render_to_response(self.template_name, context_instance=RequestContext(self.request))

    @method_decorator(user_passes_test(orientation_test))
    def dispatch(self, *args, **kwargs):
        return super(PayrollAccessView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.__render()
