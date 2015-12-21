from .base import *  # noqa @PydevCodeAnalysisIgnore


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
    'dev.resdev.calpoly.edu',
    'prod.resdev.calpoly.edu',
    '.internal.resnet.calpoly.edu',
    'clever-selects.client',
]

DEFAULT_BASE_URL = 'https://internal.resnet.calpoly.edu'

# ======================================================================================================== #
#                                      Cache Configuration                                                 #
# ======================================================================================================== #

CACHES = {
    'default': {
        'BACKEND': 'uwsgicache.UWSGICache',
        'LOCATION': get_env_variable('DJANGO_CACHE_NAME'),
    }
}
