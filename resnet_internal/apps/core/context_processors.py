"""
.. module:: resnet_internal.apps.core.context_processors
   :synopsis: ResNet Internal Core Context Processors.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from resnet_internal.apps.core.models import NavbarLink, ResNetInternalUser

from .models import TechFlair


def specializations(request):
    """Adds the user's specialization titles and display name to each context request."""

    extra_context = {}

    display_name = None
    user_specializations = []

    if request.user.is_authenticated():
        display_name = request.user.get_full_name()

        # Other Department specializations
        if request.user.is_net_admin:
            user_specializations.append('ITS Network Administrator')

        if request.user.is_telecom:
            user_specializations.append('IS Telecom Administrator')

        if request.user.is_tag_readonly:
            user_specializations.append('UH TAG Member (read-only)')

        # ResNet Titles
        if request.user.is_technician:
            user_specializations.append('ResNet Technician')

        try:
            tech = TechFlair.objects.get(tech=request.user)
        except TechFlair.DoesNotExist:
            pass
        else:
            user_specializations.append(tech.flair)

        if request.user.is_rn_staff:
            user_specializations.append('ResNet Staff')
        if request.user.is_developer:
            if "akavanau" in request.user.username:
                user_specializations.append('ResNet Development Team BDFL')
            else:
                user_specializations.append('ResNet Developer')

        if request.user.is_tag:
            user_specializations.append('UH TAG Member')

        # User is new technician (requires orientation)
        if request.user.is_new_tech:
            user_specializations = ['New ResNet Technician']

        # Empty user specializations
        if not user_specializations:
            user_specializations = ['No Specializations Available']

    # Set context
    extra_context['user_display_name'] = display_name
    extra_context['user_specializations'] = user_specializations

    return extra_context


def navbar(request):
    if isinstance(request.user, ResNetInternalUser):
        links_for_user = NavbarLink.objects.filter(groups__id__in=request.user.ad_groups.values_list('id', flat=True)).select_related()

        links_inorder = []

        for parent_link in links_for_user.filter(parent_group__isnull=True):
            links_inorder.append(parent_link)
            for link in links_for_user.filter(parent_group__id=parent_link.id).order_by('sequence_index'):
                links_inorder.append(link)
                for sublink in links_for_user.filter(parent_group__id=link.id).order_by('sequence_index'):
                    links_inorder.append(sublink)

        print(links_inorder)
        return {'navbar_links': links_inorder}
    else:
        return {}
