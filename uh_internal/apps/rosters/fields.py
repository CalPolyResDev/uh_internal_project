"""
.. module:: resnet_internal.apps.rosters.fields
   :synopsis: University Housing Internal Roster Generator Fields.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.forms.models import ModelMultipleChoiceField


class RosterBuildingChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return "{community} - {building}".format(community=obj.community,
                                                 building=obj)
