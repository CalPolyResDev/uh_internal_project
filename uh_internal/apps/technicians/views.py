"""
.. module:: resnet_internal.technicians.views
   :synopsis: University Housing Internal Technicians Views.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import logging
from operator import itemgetter

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.views.generic.edit import FormView
from ldap_groups import ADGroup

from .forms import AddADUserForm


logger = logging.getLogger(__name__)


class SingleGroupEditView(FormView):
    """Base class for viewing and editing members of an Active Directory Group."""

    template_name = "technicians/single_group_list_edit.djhtml"
    form_class = AddADUserForm
    subtitle = "AD Group Membership Editor"

    valid_user = True
    group_dn = ""
    group_name = ""
    removal_method = "remove_member"

    def __init__(self, **kwargs):
        """

        A group_dn must be supplied by the url conf initiation. A subtitle should be supplied.
        Override this with a call to FormView's __init__ to change the default behavior.

        """

        super(SingleGroupEditView, self).__init__(**kwargs)

        if not self.group_dn and "group_dn" not in kwargs:
            raise ImproperlyConfigured("'group_dn' is required as a specified init argument.")

        if not self.group_dn and "group_name" not in kwargs:
            self.group_name = self.group_dn

    def _instantiate_ad_group(self):
        """Instantiates an Active Directory group instance for modification. The group_dn is pulled from the URL conf initiation."""
        self.ad_group_instance = ADGroup(self.group_dn)

    def _get_member_info(self):
        """Gathers membership information from the instantiated ADGroup."""
        try:
            raw_member_data = self.ad_group_instance.get_member_info()
        except AttributeError:
            member_info = None
        else:
            member_info = []

            for member in raw_member_data:
                member_info.append({
                    'full_name': member['displayName'],
                    'principal_name': member['userPrincipalName'],
                    'dn': member['distinguishedName'].replace(",", ", "),  # Add spaces for better html wrapping
                    'buckley': 'FERPA' in member['distinguishedName']
                })

        if member_info:
            return sorted(member_info, key=itemgetter('principal_name'))
        else:
            return None

    def get_context_data(self, **kwargs):
        self._instantiate_ad_group()

        context = super(SingleGroupEditView, self).get_context_data(**kwargs)
        context['valid_user'] = self.valid_user
        context['subtitle'] = self.subtitle
        context['group_name'] = self.group_name
        context['group_dn'] = self.group_dn
        context['group_members'] = self._get_member_info()
        context['removal_method'] = self.removal_method

        return context

    def form_valid(self, form):
        self._instantiate_ad_group()

        if not self.valid_user:
            raise ValidationError("You do not have permission to view or modify this group.")

        principal_name = form.cleaned_data['principal_name']

        member_already_exists = False

        # Check if the user already exists in the group (when it isn't empty)
        if self._get_member_info():
            for member in self._get_member_info():
                if member['principal_name'] == principal_name:
                    member_already_exists = True

        # Don't add the user if (s)he is already in the group.
        if not member_already_exists:
            self.ad_group_instance.add_member(principal_name)
        else:
            form.add_error('principal_name', ValidationError('Cannot add ' + principal_name + ': user already exists in group.', code='user_in_group'))
            return self.form_invalid(form)

        return super(SingleGroupEditView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path


class ResTechListEditView(SingleGroupEditView):
    """Lists the members of the ResTech group. Modifications to this group will respectively modify the ResTech Admin group."""

    template_name = "technicians/restech_list_edit.djhtml"
    subtitle = "ResNet Technicians"
    group_name = "ResNet Technicians"
    group_dn = "CN=UH-RN-Techs,OU=Technology,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    removal_method = 'remove_resnet_tech'
