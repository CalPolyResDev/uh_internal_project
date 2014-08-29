"""
.. module:: resnet_internal.core.views
   :synopsis: ResNet Internal Core Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""


from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from .forms import NavigationSettingsForm
from .models import SiteAnnouncements


@login_required
def link_handler(request, mode, key, ip=""):
    # My Cal Poly Portal
    if key == "portal":
        subtitle = "My Cal Poly Portal"
        source = "https://myportal.calpoly.edu/f/u17l1s6/normal/render.uP"
    # Email
    elif key == "zimbra":
        subtitle = "Zimbra Email"
        source = "https://connect.calpoly.edu/zimbra/mail#1"
    # SRS Ticket Manager
    elif key == "srs":
        subtitle = "SRS Ticket Manager"
        source = "https://calpoly.enterprisewizard.com/gui2/cas-login?KB=calpoly2&state=Main"
    # Advocate
    elif key == "advocate":
        subtitle = "Advocate"
        source = "https://calpoly-advocate.symplicity.com/index.php/pid480522"
    # Device Pass Through
    elif key == "devices":
        subtitle = "Device Pass Through"
        source = "https://housingservices.calpoly.edu/guests/device/add/"
    # Cisco View
    elif key == "cisco":
        subtitle = "Cisco View Switch Manager"
        # Check if a specific ip was passed in
        if ip != '':
            source = "http://cp-cw-01.cp-calpoly.edu:1741/CVng/chassis.do?deviceip=" + ip + "&adhoc=yes"
        else:
            source = "http://cp-cw-01.cp-calpoly.edu:1741/CVng/chassis.do?action=-1/"
    # Aruba ClearPass
    elif key == "aruba":
        subtitle = "Aruba ClearPass"
        source = "https://clearpass.netadm.calpoly.edu/tips/tipsLogin.action"
    elif key == "ac_pcv":
        subtitle = "Aruba PCV Controller"
        source = "https://resnetcontroller1.netadm.calpoly.edu:4343"
    elif key == "ac_failover":
        subtitle = "Aruba Failover Controller"
        source = "https://resnetcontroller3.netadm.calpoly.edu:4343"
    elif key == "ac_halls":
        subtitle = "Aruba Dorms Controller"
        source = "https://resnetcontroller2.netadm.calpoly.edu:4343"
    elif key == "ac_airwaves_p":
        subtitle = "Aruba AirWaves Primary"
        source = "https://resnetairwaves1.netadm.calpoly.edu"
    elif key == "ac_airwaves_s":
        subtitle = "Aruba AirWaves Secondary"
        source = "https://resnetairwaves2.netadm.calpoly.edu"
    # CCA Manager
    elif key == "ccamgr":
        subtitle = "CCA Manager"
        source = "https://ccamgr.calpoly.edu/admin/"
    # Wiki Pages
    elif key == "resnet_wiki":
        subtitle = "ResNet Wiki"
        source = "https://wiki.calpoly.edu/display/RES/ResNet+Home"
    elif key == "housing_wiki":
        subtitle = "University Housing Wiki"
        source = "https://wiki.calpoly.edu/display/UH/University+Housing+Home"
    elif key == "its_wiki":
        subtitle = "ITS Wiki"
        source = "https://wiki.calpoly.edu/display/ITS/ITS+Home"
    elif key == "flugzeug":
        subtitle = "Django Administration"
        source = "/flugzeug/"
    # None of the passed keys are correct - return a 404
    else:
        return HttpResponseNotFound()

    if mode == "frame" or request.user.open_links_in_frame:
        if mode == "external":
            return HttpResponseRedirect(source)

        return render_to_response('core/frame.html', {'subtitle': subtitle, 'source': source}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(source)


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):

        context = super(TemplateView, self).get_context_data(**kwargs)
        context['announcements'] = SiteAnnouncements.objects.all().order_by('-created')[:3]

        return context


class NavigationSettingsView(FormView):
    template_name = "core/settings/navigation.html"
    form_class = NavigationSettingsForm

    def get_initial(self):
        initial = self.initial.copy()

        initial.update({
            'handle_links': 'frame' if self.request.user.open_links_in_frame else 'external',
        })

        return initial

    def form_valid(self, form):

        link_handling = form.cleaned_data['handle_links']

        user_instance = self.request.user
        user_instance.open_links_in_frame = True if link_handling == "frame" else False
        user_instance.save()

        return render_to_response('core/settings/close_window.html', context_instance=RequestContext(self.request))


class LoginView(FormView):
    """

    Displays the login form and handles the login action.

    Sets user's display name and specializations as session variables upon authentication:
       request.session["user_display_name"] and
       request.session["user_specializations"]

    """

    template_name = 'core/login.html'
    form_class = AuthenticationForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):

        # Authenticate the user against LDAP
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user.is_authenticated():
            auth_login(self.request, user)

        # Check if user is new tech
        if self.request.user.is_technician:
            if self.request.user.is_new_tech is None:  # First time log in, set flag from None to True
                self.request.user.is_new_tech = True
                self.request.user.save()

        if self.request.user.is_technician and self.request.user.is_new_tech:
            self.success_url = reverse_lazy('orientation_checklist')
        else:
            self.success_url = self.request.GET.get("next", reverse_lazy('home'))

        return super(LoginView, self).form_valid(form)


def logout(request):
    """Logs the current user out."""

    auth_logout(request)
    redirection = reverse_lazy('home')
    return HttpResponseRedirect(redirection)
