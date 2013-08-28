"""
.. module:: srsconnector.settings
   :synopsis: SRS Connector Settings.

.. moduleauthor:: Kyle Dodson <kdodson@caloply.edu>
.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.conf import settings

APP_NAME = 'srsconnector'

#
# Configures the SRS database alias
#
# Default: 'srs'
#
try:
    ALIAS = settings.SRS_ALIAS
except AttributeError:
    ALIAS = 'srs'

#
# Configures the SRS database models
#
# This list of models will be handled by the SRS database router when
# it is added to the "DATABASE_ROUTERS" list in the project settings. Each entry
# will be matched against the model's module name, a lower-cased version of the
# object name.
#
# If a new model is created it must be added to this list to ensure it is
# correctly routed to the SRS database.
#
# NOTE: Each model name must be in lowercase form.
#
MODELS = ('servicerequest', 'accountrequest', 'printerrequest')
