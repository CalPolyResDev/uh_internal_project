from django.conf import settings

#
# The "srsConnector" application configuration.
#
# These settings may be specified in the project settings file. Simply prefix
# each setting name with "SRS_". For example,
#
#    SRS_ALIAS = 'srs'
#
# configured in the project settings would result in,
#
#    ALIAS = 'srs'
#
# configured in the application configuration.
#
# Author: Kyle Dodson <kdodson@calpoly.edu>
# Author: Alex Kavanaugh <kavanaugh.development@outlook.com>
#

#
# Configures the RMS database alias
#
# This alias should map to the following database configuration:
#
# {
#    'ENGINE': '[projectName].srsConnector.ewiz',
#    'NAME': '', # KnowledgeBase name
#    'USER': '',
#    'PASSWORD': '',
#    'HOST': 'calpoly.enterprisewizard.com/ewws/',
#    'PORT': '443', # Web Protocol (443='https://', else 'http://)
# }
#
# Default: 'srs'
#
try:
    ALIAS = settings.SRS_ALIAS
except AttributeError:
    ALIAS = 'srs'

#
# Configures the RMS database models
#
# This list of models will be handled by the RMS database router when
# "srsConnector.routers.SRSRouter" is added to the "DATABASE_ROUTERS" list. Each entry
# will be matched against the model's module name, a lower-cased version of the
# object name.
#
# If a new model is created it must be added to this list to ensure it is
# correctly routed to the RMS database.
#
# Default: Each model object in "srsConnector.models"
#
# NOTE: Each model name MUST be in lower-case form.
#
MODELS = ('servicerequest', 'accountrequest', 'printerrequest')
