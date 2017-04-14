from .base import *  # noqa @PydevCodeAnalysisIgnore

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

print("Prod Settings Loaded!!!!")

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

LDAP_ADMIN_GROUP = 'CN=UH-RN-Staff,OU=ResNet,OU=UH,OU=Manual,OU=Groups,' + LDAP_GROUPS_BASE_DN
LDAP_DEVELOPER_GROUP = 'CN=UH-RN-DevTeam,OU=ResNet,OU=UH,OU=Manual,OU=Groups,' + LDAP_GROUPS_BASE_DN

# ======================================================================================================== #
#                                            SSH Configuration                                             #
# ======================================================================================================== #

RESNET_SWITCH_SSH_USER = get_env_variable('RESNET_INTERNAL_SWITCH_USER_DN')
RESNET_SWITCH_SSH_PASSWORD = get_env_variable('RESNET_INTERNAL_SWITCH_USER_PASSWORD')

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
    },
}
