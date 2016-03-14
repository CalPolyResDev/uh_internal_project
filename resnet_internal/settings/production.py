from .base import *  # noqa @PydevCodeAnalysisIgnore


DEBUG = False

# ======================================================================================================== #
#                                      Session/Security Configuration                                      #
# ======================================================================================================== #

# Cookie Settings
SESSION_COOKIE_NAME = 'RNINSessionID'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ======================================================================================================== #
#                                      URL Configuration                                                   #
# ======================================================================================================== #

ALLOWED_HOSTS = [
    '.internal.resnet.calpoly.edu',
    '.internal.housing.calpoly.edu',
]

DEFAULT_BASE_URL = 'https://internal.housing.calpoly.edu'

# ======================================================================================================== #
#                                      Cache Configuration                                                 #
# ======================================================================================================== #

CACHES = {
    'default': {
        'BACKEND': 'uwsgicache.UWSGICache',
        'LOCATION': get_env_variable('DJANGO_CACHE_NAME'),
    }
}
