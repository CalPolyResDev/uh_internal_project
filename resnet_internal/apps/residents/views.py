"""
.. module:: reslife_internal.apps.residents.views
   :synopsis: ResLife Internal Resident Lookup Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.views import ChainedSelectFormViewMixin
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from rmsconnector.models import ResidentProfile, StudentAddress
from rmsconnector.utils import reverse_address_lookup, Resident

from .forms import FullNameSearchForm, PrincipalNameSearchForm, AddressSearchForm


logger = logging.getLogger(__name__)


class SearchView(FormView):
    """Performs resident lookups given either a full name, cpID, or dorm address and displays the results, if any."""

    template_name = "residents/search.html"
    full_name_form_class = FullNameSearchForm
    principal_name_form_class = PrincipalNameSearchForm
    address_form_class = AddressSearchForm

    attribute_list = ["full_name", "email", "cell_phone", "dorm_phone", "address"]

    def get(self, request, *args, **kwargs):
        full_name_form = self.get_form(self.full_name_form_class)
        principal_name_form = self.get_form(self.principal_name_form_class)

        address_form_kwargs = self.get_form_kwargs()
        address_form_kwargs['user'] = self.request.user
        address_form = self.address_form_class(**address_form_kwargs)

        return self.render_to_response(self.get_context_data(full_name_form=full_name_form,
                                                             principal_name_form=principal_name_form,
                                                             address_form=address_form))

    def post(self, *args, **kwargs):
        full_name_form = self.get_form(self.full_name_form_class)
        principal_name_form = self.get_form(self.principal_name_form_class)

        address_form_kwargs = self.get_form_kwargs()
        address_form_kwargs['user'] = self.request.user
        address_form = self.address_form_class(**address_form_kwargs)

        if self.request.POST["lookup_type"] == "full_name":
            if full_name_form.is_valid():
                return self.full_name_form_valid(full_name_form)
            else:
                return self.full_name_form_invalid(full_name_form)
        elif self.request.POST["lookup_type"] == "principal_name":
            if principal_name_form.is_valid():
                return self.principal_name_form_valid(principal_name_form)
            else:
                return self.principal_name_form_invalid(principal_name_form)
        elif self.request.POST["lookup_type"] == "address":
            if address_form.is_valid():
                return self.address_form_valid(address_form)
            else:
                return self.address_form_invalid(address_form)
        else:
            return self.forms_invalid(full_name_form, principal_name_form, address_form)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        if self.request.method == "POST":
            search_results = []

            for resident in kwargs.pop('resident_list'):
                search_results.append({attribute: getattr(resident, attribute) for attribute in self.attribute_list})
                search_results.sort(key=lambda x: (x["email"]))

            context["search_results"] = search_results

        return context

    def full_name_form_valid(self, form):
        first_name = self.request.POST['first_name']
        last_name = self.request.POST['last_name']

        resident_profiles = ResidentProfile.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)

        if resident_profiles.exists():
            resident_list = []

            for resident_profile in resident_profiles:
                try:
                    principal_name = resident_profile.student_address.email
                except StudentAddress.DoesNotExist:
                    continue
                else:
                    try:
                        resident_list.append(Resident(principal_name=principal_name))
                    except ObjectDoesNotExist:
                        continue

            return self.render_to_response(self.get_context_data(full_name_form=form,
                                                                 principal_name_form=self.principal_name_form_class(),
                                                                 address_form=self.address_form_class(),
                                                                 resident_list=resident_list))
        else:
            form.add_error(field=None, error='The first and last names provided do not match University Housing records.')
            return self.full_name_form_invalid(form)

    def principal_name_form_valid(self, form):
        principal_name = self.request.POST['principal_name']

        try:
            resident_list = [Resident(principal_name=principal_name)]
        except ObjectDoesNotExist as exc:
            if str(exc).startswith("A room booking could not be found"):
                form.add_error(field=None, error="{principal_name} does not currently reside in University Housing.".format(principal_name=principal_name))
            else:
                form.add_error(field=None, error="The email address provided does not match University Housing records.")
            return self.principal_name_form_invalid(form)
        else:
            return self.render_to_response(self.get_context_data(full_name_form=self.full_name_form_class(),
                                                                 principal_name_form=form,
                                                                 address_form=self.address_form_class(),
                                                                 resident_list=resident_list))

    def address_form_valid(self, form):
        community = form.cleaned_data['community'].name
        building = form.cleaned_data['building'].name
        room = self.request.POST['room']

        try:
            resident_list = reverse_address_lookup(community=community, building=building, room=room)
        except ObjectDoesNotExist:
            form.add_error(field=None, error='The address provided does not match University Housing records or is currently vacant.')
            return self.address_form_invalid(form)
        else:
            return self.render_to_response(self.get_context_data(full_name_form=self.full_name_form_class(),
                                                                 principal_name_form=self.principal_name_form_class(),
                                                                 address_form=form,
                                                                 resident_list=resident_list))

    def full_name_form_invalid(self, full_name_form):
        return self.render_to_response(self.get_context_data(full_name_form=full_name_form,
                                                             principal_name_form=self.principal_name_form_class(),
                                                             address_form=self.address_form_class(),
                                                             resident_list=[]))

    def principal_name_form_invalid(self, principal_name_form):
        return self.render_to_response(self.get_context_data(full_name_form=self.full_name_form_class(),
                                                             principal_name_form=principal_name_form,
                                                             address_form=self.address_form_class(),
                                                             resident_list=[]))

    def address_form_invalid(self, address_form):
        return self.render_to_response(self.get_context_data(full_name_form=self.full_name_form_class(),
                                                             principal_name_form=self.principal_name_form_class(),
                                                             address_form=address_form,
                                                             resident_list=[]))

    def forms_invalid(self, full_name_form, principal_name_form, address_form):
        return self.render_to_response(self.get_context_data(full_name_form=self.full_name_form_class(),
                                                             principal_name_form=self.principal_name_form_class(),
                                                             address_form=self.address_form_class(),
                                                             resident_list=[]))
