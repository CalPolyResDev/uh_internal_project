import ldap3
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType


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


# ======================================================================================================== #
#                                         General Management                                               #
# ======================================================================================================== #

ADMINS = (
    ('Alex Kavanaugh', 'kavanaugh.development@outlook.com'),
    ('RJ Almada', 'almada.dev@gmail.com')
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
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

ROOT_URLCONF = 'resnet_internal.urls'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# ======================================================================================================== #
#                                          Database Configuration                                          #
# ======================================================================================================== #

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'resnet_internal',
        'USER': 'resnet_internal',
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_DEFAULT_PASSWORD'),
        'HOST': 'data.resdev.calpoly.edu',
        'PORT': '3306',
    },
    'common': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'common',
        'USER': 'common',
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_COMMON_PASSWORD'),
        'HOST': 'data.resdev.calpoly.edu',
        'PORT': '3306',
    },
    'printers': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'printers',
        'USER': 'printers',
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_PRINTERS_PASSWORD'),
        'HOST': 'data.resdev.calpoly.edu',
        'PORT': '3306',
    },
    'rms': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'mercprd',
        'USER': get_env_variable('RESNET_INTERNAL_DB_RMS_USERNAME'),
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_RMS_PASSWORD'),
        'HOST': 'mercprd.db.calpoly.edu',
        'PORT': '1521',
    },
    'srs': {
        'ENGINE': 'django_ewiz',
        'NAME': 'Calpoly2',
        'USER': 'resnetapi@calpoly.edu',
        'PASSWORD': get_env_variable('RESNET_INTERNAL_DB_SRS_PASSWORD'),
        'HOST': 'srs.calpoly.edu/ewws/',
        'PORT': '443',
    },
}

DATABASE_ROUTERS = (
    'resnet_internal.apps.core.routers.CommonRouter',
    'resnet_internal.apps.printerrequests.routers.PrinterRequestsRouter',
    'rmsconnector.routers.RMSRouter',
    'srsconnector.routers.SRSRouter',
)

# ======================================================================================================== #
#                                            E-Mail Configuration                                          #
# ======================================================================================================== #

# Incoming email settings
INCOMING_EMAIL = {
    'IMAP4': {  # IMAP4 is currently the only supported protocol. It must be included.
        'HOST': 'mail.calpoly.edu',  # The host to use for receiving email. Set to empty string for localhost.
        'PORT': 993,  # The port to use. Set to empty string for default values: 143, 993(SSL).
        'USE_SSL': True,  # Whether or not to use SSL (Boolean)
        'USER': get_env_variable('RESNET_INTERNAL_EMAIL_IN_USERNAME'),  # The username to use. The full email address is what most servers require.
        'PASSWORD': get_env_variable('RESNET_INTERNAL_EMAIL_IN_PASSWORD'),  # The password to use. Note that only clearText authentication is supported.
    },
}

# Outgoing email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # This configuration uses the SMTP protocol as a backend
EMAIL_HOST = 'mail.calpoly.edu'  # The host to use for sending email. Set to empty string for localhost.
EMAIL_PORT = 25  # The port to use. Defaul values: 25, 587
EMAIL_USE_TLS = True  # Whether or not to use SSL (Boolean)
EMAIL_HOST_USER = INCOMING_EMAIL['IMAP4']['USER']  # The username to use. The full email address is what most servers require.
EMAIL_HOST_PASSWORD = INCOMING_EMAIL['IMAP4']['PASSWORD']  # The password to use. Note that only clearText authentication is supported.

# Set the server's email address (for sending emails only)
SERVER_EMAIL = 'ResDev Mail Relay Server <resdev@calpoly.edu>'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# ======================================================================================================== #
#                                              Access Permissions                                          #
# ======================================================================================================== #

technician_access_test = (lambda user: user.is_developer or user.is_rn_staff or user.is_technician)
staff_access_test = (lambda user: user.is_developer or user.is_rn_staff)
developer_access_test = (lambda user: user.is_developer)

portmap_access_test = (lambda user: user.is_developer or user.is_rn_staff or user.is_technician or user.is_net_admin or user.is_telecom or user.is_tag or user.is_tag_readonly)
portmap_modify_access_test = (lambda user: user.is_developer or user.is_rn_staff or user.is_technician or user.is_net_admin or user.is_telecom or user.is_tag)

computers_access_test = (lambda user: user.is_developer or user.is_rn_staff or user.is_technician or user.is_net_admin or user.is_tag or user.is_tag_readonly)
computers_modify_access_test = (lambda user: user.is_developer or user.is_rn_staff or user.is_technician or user.is_net_admin or user.is_tag)
computer_record_modify_access_test = (lambda user: user.is_developer or user.is_net_admin or user.is_tag)

printers_access_test = computers_access_test
printers_modify_access_test = computers_modify_access_test

# ======================================================================================================== #
#                                        Authentication Configuration                                      #
# ======================================================================================================== #

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/login/'

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL = 'core.ResNetInternalUser'

AUTH_LDAP_BIND_DN = get_env_variable('RESNET_INTERNAL_LDAP_USER_DN')
AUTH_LDAP_BIND_PASSWORD = get_env_variable('RESNET_INTERNAL_LDAP_PASSWORD')

AUTH_LDAP_SERVER_URI = 'ldap://ad.calpoly.edu'
AUTH_LDAP_START_TLS = True

AUTH_LDAP_USER_SEARCH = LDAPSearch('DC=ad,DC=calpoly,DC=edu', ldap3.SEARCH_SCOPE_WHOLE_SUBTREE, '(&(objectClass=user)(sAMAccountName=%(user)s))')
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('DC=ad,DC=calpoly,DC=edu', ldap3.SEARCH_SCOPE_WHOLE_SUBTREE, '(objectClass=group)')

AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_REQUIRE_GROUP = 'CN=resnetinternal,OU=Websites,OU=Groups,OU=UH,OU=Delegated,DC=ad,DC=calpoly,DC=edu'

AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    'is_net_admin': 'StateHRDept - IS-ITS-Networks (132900 FacStf Only),OU=FacStaff,OU=StateHRDept,OU=Automated,OU=Groups,DC=ad,DC=calpoly,DC=edu',
    'is_telecom': 'StateHRDept - IS-ITS-Telecommunications (133100 FacStf Only),OU=FacStaff,OU=StateHRDept,OU=Automated,OU=Groups,DC=ad,DC=calpoly,DC=edu',
    'is_tag': 'CN=UH-TAG,OU=Groups,OU=UH,OU=Delegated,DC=ad,DC=calpoly,DC=edu',
    'is_tag_readonly': 'CN=UH-TAG-READONLY,OU=User Groups,OU=Websites,OU=Groups,OU=UH,OU=Delegated,DC=ad,DC=calpoly,DC=edu',

    'is_technician': 'CN=UH-RN-Techs,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu',
    'is_rn_staff': 'CN=UH-RN-Staff,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu',
    'is_developer': 'CN=UH-RN-DevTeam,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu',

    'is_staff': 'CN=UH-RN-DevTeam,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu',
    'is_superuser': 'CN=UH-RN-DevTeam,OU=ResNet,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu',
}

# ======================================================================================================== #
#                                        LDAP Groups Configuration                                         #
# ======================================================================================================== #

LDAP_GROUPS_SERVER_URI = 'ldap://ad.calpoly.edu'
LDAP_GROUPS_BASE_DN = 'DC=ad,DC=calpoly,DC=edu'

LDAP_GROUPS_BIND_DN = get_env_variable('RESNET_INTERNAL_LDAP_USER_DN')
LDAP_GROUPS_BIND_PASSWORD = get_env_variable('RESNET_INTERNAL_LDAP_PASSWORD')

LDAP_GROUPS_USER_LOOKUP_ATTRIBUTE = 'sAMAccountName'
LDAP_GROUPS_ATTRIBUTE_LIST = ['displayName', 'sAMAccountName', 'distinguishedName']

# ======================================================================================================== #
#                                            SSH Configuration                                             #
# ======================================================================================================== #

RESNET_SWITCH_SSH_USER = get_env_variable('RESNET_INTERNAL_LDAP_USER_DN')
RESNET_SWITCH_SSH_PASSWORD = get_env_variable('RESNET_INTERNAL_LDAP_PASSWORD')

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

# Additional locations of static files
STATICFILES_DIRS = (
    str(PROJECT_DIR.joinpath("resnet_internal", "static").resolve()),
)

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#   'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_DIRS = (
    str(PROJECT_DIR.joinpath("resnet_internal", "templates").resolve()),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'resnet_internal.apps.core.context_processors.specializations',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'django_ajax',
    'rmsconnector',
    'srsconnector',
    'django_ewiz',
    'resnet_internal.apps.core',
    'resnet_internal.apps.core.templatetags.__init__.default_app_config',
    'resnet_internal.apps.dailyduties',
    'resnet_internal.apps.datatables',
    'resnet_internal.apps.datatables.templatetags.__init__.default_app_config',
    'resnet_internal.apps.adgroups',
    'resnet_internal.apps.orientation',
    'resnet_internal.apps.computers',
    'resnet_internal.apps.portmap',
    'resnet_internal.apps.printers',
    'resnet_internal.apps.printerrequests',
    'resnet_internal.apps.printerrequests.templatetags.__init__.default_app_config',
)

# ======================================================================================================== #
#                                         Logging Configuration                                            #
# ======================================================================================================== #

RAVEN_CONFIG = {
    'dsn': get_env_variable('RESNET_INTERNAL_SENTRY_DSN'),
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
            'level': 'INFO',
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
        'django_auth_ldap': {
            'level': 'INFO',
            'handlers': ['sentry'],
            'propagate': True,
        },
        'django_ajax': {
            'level': 'INFO',
            'handlers': ['sentry'],
            'propagate': True,
        },
        'django_datatables_view': {
            'level': 'INFO',
            'handlers': ['sentry'],
            'propagate': True,
        },
        'paramiko': {
            'level': 'WARNING',
            'handlers': ['sentry'],
            'propagate': True,
        },
    }
}
