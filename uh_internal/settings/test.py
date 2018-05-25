from .local import *  # noqa @PydevCodeAnalysisIgnore


# ======================================================================================================== #
#                                          Database Configuration                                          #
# ======================================================================================================== #

DATABASES['default'] = dj_database_url.config(default=get_env_variable('RESNET_INTERNAL_DB_TEST_DATABASE_URL'))
