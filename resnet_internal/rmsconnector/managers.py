"""
.. module:: rmsconnector.managers
   :synopsis: RMS Connector Model Managers.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models import Manager, Q

from .settings import VALID_COMMUNITIES, UNNECESSARY_BUILDING_NAMES


class BuildingManager(Manager):
    """Manager for the RMS Building Model."""

    def get_query_set(self):
        """Removes unnecessary buildings from querysets."""

        first = True
        finalQFilter = None
        finalQExclude = None

        # Exclude buildings that do not belong to valid communities
        for validCommunity in VALID_COMMUNITIES:
            kwargz = {"community__community": validCommunity}
            q = Q(**kwargz)
            if (first):
                first = False
                finalQFilter = q
            else:
                finalQFilter |= q

        first = True
        # Exclude unnecessary buildings
        for buildingName in UNNECESSARY_BUILDING_NAMES:
            kwargz = {"name": buildingName}
            q = Q(**kwargz)
            if (first):
                first = False
                finalQExclude = q
            else:
                finalQExclude |= q

        return super(BuildingManager, self).get_query_set().filter(finalQFilter).exclude(finalQExclude)


class CommunityManager(Manager):
    """Manager for the RMS Community Model."""

    def get_query_set(self):
        """Only returns valid Communities, as described in settings."""

        first = True
        finalQ = None

        for validCommunity in VALID_COMMUNITIES:
            kwargz = {"community": validCommunity}
            q = Q(**kwargz)
            if (first):
                first = False
                finalQ = q
            else:
                finalQ |= q

        return super(CommunityManager, self).get_query_set().filter(finalQ)
