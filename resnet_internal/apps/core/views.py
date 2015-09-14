"""
.. module:: resnet_internal.apps.core.views
   :synopsis: ResNet Internal Core Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import datetime

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.template.context import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from srsconnector.models import ServiceRequest

from .forms import AutoFocusAuthenticationForm
from .models import SiteAnnouncements


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):

        context = super(TemplateView, self).get_context_data(**kwargs)
        context['announcements'] = SiteAnnouncements.objects.all().order_by('-created')[:3]

        return context


class TicketSummaryView(TemplateView):
    template_name = 'core/ticket_summary.html'

    def get_context_data(self, **kwargs):
        context = super(TicketSummaryView, self).get_context_data(**kwargs)
        ticket_id = kwargs['ticket_id']
        context['ticket'] = ServiceRequest.objects.get(ticket_id=ticket_id)

        time_difference = (datetime.today() - context['ticket'].date_updated).total_seconds() / 86400

        if time_difference < 3:
            context['date_display_class'] = 'text-success'
        elif time_difference < 7:
            context['date_display_class'] = 'text-info'
        elif time_difference < 14:
            context['date_display_class'] = 'text-warning'
        else:
            context['date_display_class'] = 'text-danger'

        return context


class LoginView(FormView):
    """

    Displays the login form and handles the login action.

    Sets user's display name and specializations as session variables upon authentication:
       request.session["user_display_name"] and
       request.session["user_specializations"]

    """

    template_name = 'core/login.html'
    form_class = AutoFocusAuthenticationForm

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


def handler500(request):
    """500 error handler which includes ``request`` in the context."""

    from django.template import loader
    from django.http import HttpResponseServerError

    template = loader.get_template('500.html')

    return HttpResponseServerError(template.render(RequestContext(request)))
