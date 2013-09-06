"""
.. module:: resnet_internal.core.views
   :synopsis: ResNet Internal Core Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""


from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy


@login_required
def link_handler(request, mode, key, ip=""):
    # My Cal Poly Portal
    if key == "portal":
        subtitle = "My Cal Poly Portal"
        source = "https://myportal.calpoly.edu/f/u17l1s6/normal/render.uP"
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
        # Check if a specific ip was passed in
        if ip != '':
            source = "http://cp-cw-01.cp-calpoly.edu:1741/CVng/chassis.do?deviceip=" + ip + "&adhoc=yes"
        else:
            source = "http://cp-cw-01.cp-calpoly.edu:1741/CVng/chassis.do?action=-1/"
    # Aruba ClearPass
    elif key == "aruba":
        subtitle = "Aruba ClearPass"
        source = "https://resnetclearpass.netadm.calpoly.edu/"
    # CCA Manager
    elif key == "ccamgr":
        subtitle = "CCA Manager"
        source = "https://ccamgr.calpoly.edu/admin/"
    # ResNet Wiki
    elif key == "wiki":
        subtitle = "ResNet Wiki"
        source = "https://resnet.calpoly.edu/wiki/"
    # None of the passed keys are correct - return a 404
    else:
        return HttpResponseNotFound()

# Go to the link directly until the frame issues are sorted out.
    return HttpResponseRedirect(source)
#    return render_to_response('core/frame.html', {'subtitle': subtitle, 'source': source}, context_instance=RequestContext(request))


class IndexView(TemplateView):
    template_name = "core/index.html"


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
            if self.request.user.is_new_tech == None:  # First time log in, set flag from None to True
                self.request.user.is_new_tech = True
                self.request.user.save()

        # Set user session variables
        display_name = self.request.user.get_full_name()
        user_specializations = []

        # Other Department specializations
        if self.request.user.is_net_admin:
            user_specializations.append('ITS Network Administrator')

        if self.request.user.is_telecom:
            user_specializations.append('IS Telecom Administrator')

        # ResNet Titles
        if self.request.user.is_technician:
            user_specializations.append('ResNet Technician')
        if self.request.user.is_network_analyst:
            user_specializations.append('Network Analyst')
        if self.request.user.is_domain_manager:
            user_specializations.append('Domain Manager')
        if self.request.user.is_osd:
            user_specializations.append('OS Deployer')
        if self.request.user.is_uhtv:
            user_specializations.append('UHTV Staff')
        if self.request.user.is_drupal:
            user_specializations.append('ResNet Drupal Admin')
        if self.request.user.is_rn_staff:
            user_specializations.append('ResNet Staff')
        if self.request.user.is_developer:
            user_specializations.append('ResNet Developer')

        if self.request.user.is_tag:
            user.specializations.append('UH TAG Member')

        # User is new technician (requires orientation)
        if self.request.user.is_new_tech:
            user_specializations = ['New ResNet Technician']

        # Empty user specializations
        if not user_specializations:
            user_specializations = ['No Specializations Available']

        # Set session variables
        self.request.session['user_display_name'] = display_name
        self.request.session['user_specializations'] = user_specializations

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        """Generate a success url. If the user is a new technician, send him/her to orientation."""

        success_url = reverse_lazy('home')

        if self.request.user.is_new_tech:
            success_url = reverse_lazy('orientation-checklist')

        return success_url


def logout(request):
    """Logs the current user out."""

    auth_logout(request)
    redirection = reverse_lazy('home')
    return HttpResponseRedirect(redirection)
