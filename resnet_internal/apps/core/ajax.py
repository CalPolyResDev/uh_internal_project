"""
.. module:: resnet_internal.apps.core.ajax
   :synopsis: ResNet Internal Core AJAX Methods.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging

from django.views.decorators.http import require_POST

from django_ajax.decorators import ajax
from rmsconnector.constants import (SIERRA_MADRE, YOSEMITE, SOUTH_MOUNTAIN, NORTH_MOUNTAIN,
                                    CERRO_VISTA, POLY_CANYON_VILLAGE, SIERRA_MADRE_BUILDINGS, YOSEMITE_BUILDINGS,
                                    SOUTH_MOUNTAIN_BUILDINGS, NORTH_MOUNTAIN_BUILDINGS, CERRO_VISTA_BUILDINGS,
                                    POLY_CANYON_VILLAGE_BUILDINGS)

logger = logging.getLogger(__name__)


@ajax
@require_POST
def update_building(request):
    """ Update building drop-down choices based on the community chosen.

    :param community: The community for which to display building choices.
    :type community: str
    :param building_selection: The building selected before form submission.
    :type building_selection: str

    """

    # Pull post parameters
    community = request.POST.get("community", None)
    building_selection = request.POST.get("building_selection", None)

    building_options = {
        SIERRA_MADRE: [(building, building) for building in SIERRA_MADRE_BUILDINGS],
        YOSEMITE: [(building, building) for building in YOSEMITE_BUILDINGS],
        SOUTH_MOUNTAIN: [(building, building) for building in SOUTH_MOUNTAIN_BUILDINGS],
        NORTH_MOUNTAIN: [(building, building) for building in NORTH_MOUNTAIN_BUILDINGS],
        CERRO_VISTA: [(building, building) for building in CERRO_VISTA_BUILDINGS],
        POLY_CANYON_VILLAGE: [(building, building) for building in POLY_CANYON_VILLAGE_BUILDINGS],
    }
    choices = []

    # Add options iff a building is selected
    if community:
        for value, label in building_options[str(community)]:
            if building_selection and value == building_selection:
                choices.append("<option value='%s' selected='selected'>%s</option>" % (value, label))
            else:
                choices.append("<option value='%s'>%s</option>" % (value, label))
    else:
        logger.debug("A building wasn't passed via POST.")
        choices.append("<option value='%s'>%s</option>" % ("", "---------"))

    data = {
        'inner-fragments': {
            '#id_building': ''.join(choices),
        },
    }

    return data
