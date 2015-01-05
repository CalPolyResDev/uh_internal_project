from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# ======================================================================================================== #
#                                      Session/Security Configuration                                      #
# ======================================================================================================== #

# Cookie Settings
SESSION_COOKIE_NAME = 'RNINSessionID'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    '.internal.resnet.calpoly.edu',
]
