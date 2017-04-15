from .base import *  # noqa @PydevCodeAnalysisIgnore


# ======================================================================================================== #
#                                          Database Configuration                                          #
# ======================================================================================================== #

DATABASES = {
    'default': dj_database_url.config(default=get_env_variable('RESNET_INTERNAL_DB_TEST_DATABASE_URL'))
}

#DBBACKUP_DATABASES = ['default']

#DATABASES['default']['DBBACKUP_BACKUP_COMMAND_EXTRA_ARGS'] = ['--exclude-table-data=network_clearpassloginattempt']
