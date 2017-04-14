import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
import raven

def get_env_variable(name):
    """ Gets the specified environment variable.

    :param name: The name of the variable.
    :type name: str
    :returns: The value of the specified variable.
    :raises: **ImproperlyConfigured** when the specified variable does not exist.

    """

    try:
        return os.environ[name]
    except KeyError:
        error_msg = "The %s environment variable is not set!" % name
        raise ImproperlyConfigured(error_msg)


def string_to_bool(string):
    """ Used for converting environment variable strings to booleans.

    Aims to be as robust as possible by covering most of the commonly used ones.
    """

    if string.lower().strip() in ['true', '1', 't', 'y', 'yes']:
        return True

    return False

# ======================================================================================================== #
#                                         General Settings                                                 #
# ======================================================================================================== #

# Local time zone for this installation. Choices can be found here:
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation.
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

DATE_FORMAT = 'l, F d, Y'

TIME_FORMAT = 'h:i a'

DATETIME_FORMAT = 'l, F d, Y h:i a'

DEFAULT_CHARSET = 'utf-8'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Must be larger than largest allowed attachment size or attachments will break.
# This is because non-in-memory file objects can't be serialized for the cache.
FILE_UPLOAD_MAX_MEMORY_SIZE = 1048576 * 21  # 21 MiB

MAIN_APP_NAME = 'uh_internal'

# ======================================================================================================== #
#                                         General Management                                               #
# ======================================================================================================== #

ADMINS = (
    ('ResDev', 'resdev@calpoly.edu'),
)

MANAGERS = ADMINS

# ======================================================================================================== #
#                                      URL Configuration                                                   #
# ======================================================================================================== #

ROOT_URLCONF = MAIN_APP_NAME + '.urls'
DEFAULT_BASE_URL = get_env_variable('RESNET_INTERNAL_DEFAULT_BASE_URL')

# ======================================================================================================== #
#                                              Access Permissions                                          #
# ======================================================================================================== #

DEVELOPER_ACCESS = 'developer'
TICKET_ACCESS = 'ticket'
ROOMS_ACCESS = 'rooms'
ROOMS_MODIFY_ACCESS = 'rooms_modify'
DAILY_DUTIES_ACCESS = 'daily_duties'
ORIENTATION_ACCESS = 'orientation'
TECHNICIAN_LIST_ACCESS = 'technician_list'
NETWORK_ACCESS = 'network'
NETWORK_MODIFY_ACCESS = 'network_modify'
COMPUTERS_ACCESS = 'computers'
COMPUTERS_MODIFY_ACCESS = 'computers_modify'
COMPUTERS_RECORD_MODIFY_ACCESS = 'computers_record_modify'
PRINTERS_ACCESS = 'printers'
PRINTERS_MODIFY_ACCESS = 'printers_modify'
CSD_ASSIGNMENT_ACCESS = 'csd_assignment'
ROSTER_ACCESS = 'roster'
RESIDENT_LOOKUP_ACCESS = 'resident_lookup'
PRINTER_REQUEST_CREATE_ACCESS = 'printer_request_create'

ACCESS_PERMISSIONS = [
    DEVELOPER_ACCESS,
    TICKET_ACCESS,
    ROOMS_ACCESS,
    ROOMS_MODIFY_ACCESS,
    DAILY_DUTIES_ACCESS,
    ORIENTATION_ACCESS,
    TECHNICIAN_LIST_ACCESS,
    NETWORK_ACCESS,
    NETWORK_MODIFY_ACCESS,
    COMPUTERS_ACCESS,
    COMPUTERS_MODIFY_ACCESS,
    COMPUTERS_RECORD_MODIFY_ACCESS,
    PRINTERS_ACCESS,
    PRINTERS_MODIFY_ACCESS,
    CSD_ASSIGNMENT_ACCESS,
    ROSTER_ACCESS,
    RESIDENT_LOOKUP_ACCESS,
    PRINTER_REQUEST_CREATE_ACCESS,
]

# ======================================================================================================== #
#                                      Session/Security Configuration                                      #
# ======================================================================================================== #

# Cookie settings.
SESSION_COOKIE_HTTPONLY = True

# Session expiraton
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = get_env_variable('RESNET_INTERNAL_SECRET_KEY')

# ======================================================================================================== #
#                                  File/Application Handling Configuration                                 #
# ======================================================================================================== #

PROJECT_DIR = Path(__file__).parents[2]

# The directory that will hold any files for data imports from management commands.
IMPORT_DATA_PATH = PROJECT_DIR.joinpath("import_data")

# The directory that will hold user-uploaded files.
MEDIA_ROOT = str(PROJECT_DIR.joinpath("media").resolve())

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL = '/media/'

# The directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = str(PROJECT_DIR.joinpath("static").resolve())

# URL prefix for static files. Make sure to use a trailing slash.
STATIC_URL = '/static/'

STATIC_PRECOMPILER_OUTPUT_DIR = ""
STATIC_PRECOMPILER_PREPEND_STATIC_URL = True

# Additional locations of static files
STATICFILES_DIRS = (
    str(PROJECT_DIR.joinpath(MAIN_APP_NAME, "static").resolve()),
)

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
)

# The directory that will hold database backups on the application server.
DBBACKUP_BACKUP_DIRECTORY = str(PROJECT_DIR.joinpath("backups").resolve())

# Django-JS-Reverse Variable Name
JS_REVERSE_JS_VAR_NAME = 'DjangoReverse'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(PROJECT_DIR.joinpath(MAIN_APP_NAME, "templates").resolve()),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                MAIN_APP_NAME + '.apps.core.context_processors.specializations',
                MAIN_APP_NAME + '.apps.core.context_processors.navbar',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    MAIN_APP_NAME + '.apps.orientation.middleware.OrientationRedirectMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_cas_ng',
    'raven.contrib.django.raven_compat',
    'django_ajax',
    'static_precompiler',
    'rmsconnector',
    'srsconnector',
    'django_ewiz',
    'paramiko',
    'jfu',
    'dbbackup',
    'clever_selects',
    'crispy_forms',
    'django_js_reverse',
    MAIN_APP_NAME + '.apps.core',
    MAIN_APP_NAME + '.apps.core.templatetags.__init__.default_app_config',
    MAIN_APP_NAME + '.apps.dailyduties',
    MAIN_APP_NAME + '.apps.datatables',
    MAIN_APP_NAME + '.apps.datatables.templatetags.__init__.default_app_config',
    MAIN_APP_NAME + '.apps.technicians',
    MAIN_APP_NAME + '.apps.orientation',
    MAIN_APP_NAME + '.apps.computers',
    MAIN_APP_NAME + '.apps.network',
    MAIN_APP_NAME + '.apps.printers',
    MAIN_APP_NAME + '.apps.printerrequests',
    MAIN_APP_NAME + '.apps.printerrequests.templatetags.__init__.default_app_config',
    MAIN_APP_NAME + '.apps.residents',
    MAIN_APP_NAME + '.apps.rosters',
)
