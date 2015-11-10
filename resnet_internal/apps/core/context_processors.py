"""
.. module:: resnet_internal.apps.core.context_processors
   :synopsis: ResNet Internal Core Context Processors.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.cache import cache

from resnet_internal.apps.core.models import NavbarLink, ResNetInternalUser

from .models import TechFlair


def specializations(request):
    """Adds the user's specialization titles and display name to each context request."""

    extra_context = {}

    display_name = None
    user_specializations = []

    if request.user.is_authenticated() and not request.is_ajax():
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
    if request.user.is_authenticated() and not request.is_ajax():
        cache_key = request.user.username + ':navbar'

        navbar = cache.get(cache_key)

        if not navbar:
            links_for_user = NavbarLink.objects.filter(groups__id__in=request.user.ad_groups.values_list('id', flat=True)).distinct()
            navbar = ''

            def a_inner_html(link):
                return '<img class="link-icon" aria-hidden="true" src="' + static(link.icon) + '" height="16">' + link.display_name

            for parent_link in links_for_user.filter(parent_group__isnull=True).order_by('sequence_index'):
                navbar = navbar + '<div class="link-group-heading">' + parent_link.display_name + '</div>\n<div class="link-group">\n<ul>\n'

                for link in links_for_user.filter(parent_group__id=parent_link.id).order_by('sequence_index'):
                    navbar = navbar + '<li>'

                    if link.is_link_group:
                        onclick_text = 'onclick="' + ('toggle_sublinks(\'#' + link.html_id + '_list\')' if not link.onclick else link.onclick) + '" '
                        navbar = navbar + '<a id="' + link.html_id + '_link" ' + (onclick_text if not link.url else 'href="' + link.url + '" ') + '>' + a_inner_html(link) + '</a>\n'
                        navbar = navbar + '</li>\n'
                        navbar = navbar + '<ul id="' + link.html_id + '_list" ' + ('style="display: none;"' if not link.url and not link.onclick else '') + '>\n'

                        for sublink in links_for_user.filter(parent_group__id=link.id).order_by('sequence_index'):
                            navbar = navbar + '<li><a ' + ('onclick="' + sublink.onclick + '" ' if sublink.onclick else '') + ((' href="' + sublink.url + '"') if sublink.url else '') + ' target="' + sublink.target + '">' + sublink.display_name + '</a></li>\n'

                        navbar = navbar + '</ul>\n'
                    else:
                        navbar = navbar + '<a id="' + link.html_id + '_link"' + (('onclick="' + link.onclick + '"') if link.onclick else '') + \
                            (('href="' + link.url + '"') if link.url else '') + 'target="' + link.target + '">\n' + a_inner_html(link) + '</a>\n'
                        navbar = navbar + '</li>\n'

                navbar = navbar + '</ul>\n</div>\n'

            cache.set(cache_key, navbar, 60 * 60 * 4)

        return {'navbar': navbar}
    else:
        return {}
