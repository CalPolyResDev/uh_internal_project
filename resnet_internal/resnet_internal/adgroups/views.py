"""
.. module:: reslife_internal.adgroups.views
   :synopsis: ResLife Internal AD Group Management Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

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

    template_name = "adgroups/single_group_list_edit.html"
    form_class = AddADUserForm
    subtitle = u"AD Group Membership Editor"

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

        if not self.group_dn and not "group_dn" in kwargs:
            raise ImproperlyConfigured("'group_dn' is required as a specified init argument.")

        if not self.group_dn and not "group_name" in kwargs:
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
                    'alias': member['sAMAccountName'],
                    'dn': member['distinguishedName'].replace(",", ", "),  # Add spaces for better html wrapping
                    'buckley': 'FERPA' in member['distinguishedName']
                })

        if member_info:
            return sorted(member_info, key=itemgetter('alias'))
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

        alias = form.cleaned_data['alias']

        member_already_exists = False

        # Check if the user already exists in the group (when it isn't empty)
        if self._get_member_info():
            for member in self._get_member_info():
                if member['alias'] == alias:
                    member_already_exists = True

        # Don't add the user if (s)he is already in the group.
        if not member_already_exists:
            self.ad_group_instance.add_member(alias)

        return super(SingleGroupEditView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path


class ResTechListEditView(SingleGroupEditView):
    "Lists the members of the ResTech group. Modifications to this group will respectively modify the ResTech Admin group."""

    template_name = "adgroups/restech_list_edit.html"
    subtitle = u"ResNet Technicians"
    group_name = u"ResNet Technicians"
    group_dn = "CN=UH-RN-Techs,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    removal_method = 'remove_resnet_tech'
