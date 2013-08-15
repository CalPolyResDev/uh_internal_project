"""
.. module:: rmsconnector.settings
   :synopsis: RMS Connector Settings.

.. moduleauthor:: Kyle Dodson <kdodson@caloply.edu>
.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings

from .constants import COMMUNITIES

APP_NAME = 'rmsconnector'

#
# Configures the RMS database alias
#
# Default: 'rms'
#
try:
    ALIAS = settings.RMS_ALIAS
except AttributeError:
    ALIAS = 'rms'

#
# Configures the RMS database models
#
# This list of models will be handled by the RMS database router when
# it is added to the "DATABASE_ROUTERS" list in the project settings. Each entry
# will be matched against the model's module name, a lower-cased version of the
# object name.
#
# If a new model is created it must be added to this list to ensure it is
# correctly routed to the RMS database.
#
# NOTE: Each model name must be in lowercase form.
#
MODELS = ('studentprofile', 'studentaddress', 'residentprofile', 'roombookings', 'roomconfigs', 'room', 'floorsection', 'floor', 'building', 'community', 'buckleyflag', 'buckleyflagid', 'termdates')


#
# RMS Valid Communities
#
# This is a list of Community Names (from the Community model) to be considered valid.
#
# If a Community's name is not in this list, it is considered invalid and will not be included
# in database lookups.
#
VALID_COMMUNITIES = COMMUNITIES

#
# RMS Unnecessary Building Names
#
# This is a list of Building Names (from the Building model) that should be excluded in database lookups
#
UNNECESSARY_BUILDING_NAMES = ('Sierra Madre Hall', 'Yosemite Hall', 'Poly Canyon Village')
