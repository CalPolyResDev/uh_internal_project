"""
.. module:: resnet_internal.core.context_processors
   :synopsis: ResNet Internal Core Context Processors.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""


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

        # ResNet Titles
        if request.user.is_technician:
            user_specializations.append('ResNet Technician')
        if request.user.is_uhtv:
            user_specializations.append('UHTV Staff')
        if request.user.is_rn_staff:
            user_specializations.append('ResNet Staff')
        if request.user.is_developer:
            user_specializations.append('ResNet Developer')

        if "akavanau" in request.user.username:
            user_specializations.append('ResDev BDFL')

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
