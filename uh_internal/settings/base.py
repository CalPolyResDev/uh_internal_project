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
#                                         General Management                                               #
# ======================================================================================================== #

ADMINS = (
    ('ResDev', 'resdev@calpoly.edu'),
)

MANAGERS = ADMINS

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

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Must be larger than largest allowed attachment size or attachments will break.
# This is because non-in-memory file objects can't be serialized for the cache.
FILE_UPLOAD_MAX_MEMORY_SIZE = 1048576 * 21  # 21 MiB

MAIN_APP_NAME = 'uh_internal'

# ======================================================================================================== #
#                                      URL Configuration                                                   #
# ======================================================================================================== #

ROOT_URLCONF = MAIN_APP_NAME + '.urls'
DEFAULT_BASE_URL = get_env_variable('RESNET_INTERNAL_DEFAULT_BASE_URL')

# ======================================================================================================== #
#                                          Database Configuration                                          #
# ======================================================================================================== #

DATABASES = {
    'default': dj_database_url.config(default=get_env_variable('RESNET_INTERNAL_DB_DEFAULT_DATABASE_URL')),
    'rms': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'mercprd.db.calpoly.edu:1521/mercprd',
        'USER': get_env_variable('RESNET_INTERNAL_DB_RMS_USERNAME'),
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_RMS_PASSWORD'),
        'OPTIONS': {'threaded': True},
    },
    'srs': {
        'ENGINE': 'django_ewiz',
        'NAME': 'Calpoly2',
        'USER': 'resnetapi@calpoly.edu',
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_SRS_PASSWORD'),
        'HOST': 'srs.calpoly.edu/ewws/',
        'PORT': '443',
        'NUM_CONNECTIONS': 40,
    },
}

DATABASE_ROUTERS = (
    'rmsconnector.routers.RMSRouter',
    'srsconnector.routers.SRSRouter',
)

DBBACKUP_DATABASES = ['default']

DATABASES['default']['DBBACKUP_BACKUP_COMMAND_EXTRA_ARGS'] = ['--exclude-table-data=network_clearpassloginattempt']

# ======================================================================================================== #
#                                            E-Mail Configuration                                          #
# ======================================================================================================== #

# Incoming email settings
INCOMING_EMAIL = {
    'IMAP4': {  # IMAP4 is currently the only supported protocol. It must be included.
        'HOST': get_env_variable('RESNET_INTERNAL_EMAIL_IN_HOST'),  # The host to use for receiving email. Set to empty string for localhost.
        'PORT': int(get_env_variable('RESNET_INTERNAL_EMAIL_IN_PORT')),  # The port to use. Set to empty string for default values: 143, 993(SSL).
        'USE_SSL': True if get_env_variable('RESNET_INTERNAL_EMAIL_IN_SSL') == "True" else False,  # Whether or not to use SSL (Boolean)
        'USER': get_env_variable('RESNET_INTERNAL_EMAIL_IN_USERNAME'),  # The username to use. The full email address is what most servers require.
        'PASSWORD': get_env_variable('RESNET_INTERNAL_EMAIL_IN_PASSWORD'),  # The password to use. Note that only clearText authentication is supported.
    },
}

# Outgoing email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # This configuration uses the SMTP protocol as a backend
EMAIL_HOST = get_env_variable('RESNET_INTERNAL_EMAIL_OUT_HOST')  # The host to use for sending email. Set to empty string for localhost.
EMAIL_PORT = int(get_env_variable('RESNET_INTERNAL_EMAIL_OUT_PORT'))  # The port to use. Defaul values: 25, 587
EMAIL_USE_TLS = True if get_env_variable('RESNET_INTERNAL_EMAIL_OUT_TLS') == "True" else False  # Whether or not to use SSL (Boolean)
EMAIL_HOST_USER = get_env_variable('RESNET_INTERNAL_EMAIL_OUT_USERNAME')  # The username to use. The full email address is what most servers require.
EMAIL_HOST_PASSWORD = get_env_variable('RESNET_INTERNAL_EMAIL_OUT_PASSWORD')  # The password to use. Note that only clearText authentication is supported.

# Set the server's email address (for sending emails only)
SERVER_EMAIL = 'ResDev Mail Relay Server <resdev@calpoly.edu>'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# ======================================================================================================== #
#                                            Slack Configuration                                           #
# ======================================================================================================== #

SLACK_WEBHOOK_URL = get_env_variable('RESNET_INTERNAL_SLACK_WEBHOOK_URL')
SLACK_VM_CHANNEL = get_env_variable('RESNET_INTERNAL_SLACK_VM_CHANNEL')
SLACK_EMAIL_CHANNEL = get_env_variable('RESNET_INTERNAL_SLACK_EMAIL_CHANNEL')
SLACK_NETWORK_STATUS_CHANNEL = get_env_variable('RESNET_INTERNAL_SLACK_NETWORK_STATUS_CHANNEL')

# ======================================================================================================== #
#                                      Network Devices Configuration                                       #
# ======================================================================================================== #

AIRWAVES = {
    'url': get_env_variable('RESNET_INTERNAL_AIRWAVES_URL'),
    'username': get_env_variable('RESNET_INTERNAL_AIRWAVES_USERNAME'),
    'password': get_env_variable('RESNET_INTERNAL_AIRWAVES_PASSWORD'),
    'verify_ssl': string_to_bool(get_env_variable('RESNET_INTERNAL_AIRWAVES_VERIFY_SSL')),
}

CLEARPASS = {
    'url': get_env_variable('RESNET_INTERNAL_CLEARPASS_URL'),
    'username': get_env_variable('RESNET_INTERNAL_CLEARPASS_USERNAME'),
    'password': get_env_variable('RESNET_INTERNAL_CLEARPASS_PASSWORD'),
    'verify_ssl': string_to_bool(get_env_variable('RESNET_INTERNAL_CLEARPASS_VERIFY_SSL')),
}

CLEARPASS_SERVERS = [
    '207.62.169.213',  # ResNet ClearPass
    '129.65.1.151',  # Backup ClearPass
    '207.62.169.214',  # Backup ClearPass 2
    '207.62.169.215',  # Backup ClearPass 3
    '129.65.1.150',  # Campus ClearPass
]

CLEARPASS_SERVICE_IGNORE = [
    'SLO_AIRGROUP_AUTH_SERVICE',
]

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
]


# ======================================================================================================== #
#                                        Authentication Configuration                                      #
# ======================================================================================================== #

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/login/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    MAIN_APP_NAME + '.apps.core.backends.CASLDAPBackend',
)

AUTH_USER_MODEL = 'core.UHInternalUser'

CAS_ADMIN_PREFIX = "flugzeug/"
CAS_LOGOUT_COMPLETELY = False
CAS_LOGIN_MSG = None
CAS_LOGGED_MSG = None

CAS_SERVER_URL = "https://my.calpoly.edu/cas/"
CAS_LOGOUT_URL = "https://my.calpoly.edu/cas/casClientLogout.jsp?logoutApp=University%20Housing%20Internal"

RESTRICT_LOGIN_TO_DEVELOPERS = string_to_bool(get_env_variable('RESNET_INTERNAL_RESTRICT_LOGIN_TO_DEVELOPERS'))

# ======================================================================================================== #
#                                        LDAP Groups Configuration                                         #
# ======================================================================================================== #

LDAP_GROUPS_SERVER_URI = 'ldap://ad.calpoly.edu'
LDAP_GROUPS_BASE_DN = 'DC=ad,DC=calpoly,DC=edu'
LDAP_GROUPS_USER_BASE_DN = 'OU=People,OU=Enterprise,OU=Accounts,' + LDAP_GROUPS_BASE_DN

LDAP_GROUPS_USER_SEARCH_BASE_DN = 'OU=Enterprise,OU=Accounts,' + LDAP_GROUPS_BASE_DN
LDAP_GROUPS_GROUP_SEARCH_BASE_DN = 'OU=Groups,' + LDAP_GROUPS_BASE_DN

LDAP_GROUPS_BIND_DN = get_env_variable('RESNET_INTERNAL_LDAP_USER_DN')
LDAP_GROUPS_BIND_PASSWORD = get_env_variable('RESNET_INTERNAL_LDAP_PASSWORD')

LDAP_GROUPS_USER_LOOKUP_ATTRIBUTE = 'userPrincipalName'
LDAP_GROUPS_GROUP_LOOKUP_ATTRIBUTE = 'name'
LDAP_GROUPS_ATTRIBUTE_LIST = ['displayName', LDAP_GROUPS_USER_LOOKUP_ATTRIBUTE, 'distinguishedName']

LDAP_ADMIN_GROUP = 'CN=UH-RN-Staff,OU=Technology,OU=UH,OU=Manual,OU=Groups,' + LDAP_GROUPS_BASE_DN
LDAP_DEVELOPER_GROUP = 'CN=UH-RN-DevTeam,OU=Technology,OU=UH,OU=Manual,OU=Groups,' + LDAP_GROUPS_BASE_DN

# ======================================================================================================== #
#                                            SSH Configuration                                             #
# ======================================================================================================== #

RESNET_SWITCH_SSH_USER = get_env_variable('RESNET_INTERNAL_SWITCH_USER_DN')
RESNET_SWITCH_SSH_PASSWORD = get_env_variable('RESNET_INTERNAL_SWITCH_USER_PASSWORD')

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
    'clever_selects',
    'crispy_forms',
    'dbbackup',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_cas_ng',
    'django_ewiz',
    'django_js_reverse',
    'jfu',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rmsconnector',
    'srsconnector',
    'static_precompiler',
    'paramiko',
    MAIN_APP_NAME + '.apps.computers',
    MAIN_APP_NAME + '.apps.core',
    MAIN_APP_NAME + '.apps.core.templatetags.__init__.default_app_config',
    MAIN_APP_NAME + '.apps.dailyduties',
    MAIN_APP_NAME + '.apps.datatables',
    MAIN_APP_NAME + '.apps.datatables.templatetags.__init__.default_app_config',
    MAIN_APP_NAME + '.apps.network',
    MAIN_APP_NAME + '.apps.orientation',
    MAIN_APP_NAME + '.apps.printers',
    MAIN_APP_NAME + '.apps.residents',
    MAIN_APP_NAME + '.apps.rosters',
    MAIN_APP_NAME + '.apps.technicians',
)

# ======================================================================================================== #
#                                         Logging Configuration                                            #
# ======================================================================================================== #

RAVEN_CONFIG = {
    'dsn': get_env_variable('RESNET_INTERNAL_SENTRY_DSN'),
    'release': raven.fetch_git_sha(str(PROJECT_DIR.resolve())),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'DEBUG',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
