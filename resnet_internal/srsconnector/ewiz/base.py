from djangotoolbox.base import (NonrelDatabaseFeatures,
                                NonrelDatabaseOperations,
                                NonrelDatabaseWrapper,
                                NonrelDatabaseClient,
                                NonrelDatabaseValidation,
                                NonrelDatabaseIntrospection,
                                NonrelDatabaseCreation)

#
# The EnterpriseWizard database backend base
#
# Author: Alex Kavanaugh
# Email: kavanaugh.development@outlook.com
#

class DatabaseOperations(NonrelDatabaseOperations):
    compiler_module = __name__.rsplit('.', 1)[0] + '.compiler'

class DatabaseWrapper(NonrelDatabaseWrapper):
    operators = {
        'exact': "= BINARY '%s'",
        'iexact': "= '%s'",
        'contains': "LIKE BINARY '%%25%s%%25'",
        'icontains': "LIKE '%%25%s%%25'",
        'regex': "REGEXP BINARY '%s'",
        'iregex': "REGEXP '%s'",
        'gt': "> '%s'",
        'gte': ">= '%s'",
        'lt': "< '%s'",
        'lte': "<= '%s'",
        'startswith': "LIKE BINARY '%s%%25'",
        'endswith': "LIKE BINARY '%%25%s'",
        'istartswith': "LIKE '%s%%25'",
        'iendswith': "LIKE '%%25%s'",
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.server_version = None
        self.features = NonrelDatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.client = NonrelDatabaseClient(self)
        self.creation = NonrelDatabaseCreation(self)
        self.introspection = NonrelDatabaseIntrospection(self)
        self.validation = NonrelDatabaseValidation(self)
