from settings import ALIAS
from settings import MODELS

#
# A database router to control interactions with the EnterpriseWizard REST interface.
#
# This router supports reads, writes, but disables relations and "syncdb" for
# the models listed in "SRS_MODELS".
#
class SRSRouter(object):

    #
    # Shortcut to return a model's application label
    #
    def _app(self, model):
        return model._meta.app_label

    #
    # Shortcut to return a model's module name, a lower-cased version of its object name
    #
    def _mod(self, model):
        return model._meta.module_name

    #
    # Returns a database match if the model matches a "srsConnector" model
    #
    def db_for_read(self, model, **hints):
        if self._app(model) == 'srsconnector' and self._mod(model) in MODELS:
            return ALIAS
        return None

    #
    # Returns a database match if the model matches a "srsConnector" model
    #
    def db_for_write(self, model, **hints):
        if self._app(model) == 'srsconnector' and self._mod(model) in MODELS:
            return ALIAS
        return None

    #
    # Provides no constraints on relationships
    #
    def allow_relation(self, obj1, obj2, **hints):
        return None

    #
    # Forbids table synchronization for "srsConnector" models
    #
    def allow_syncdb(self, db, model):
        if self._app(model) == 'srsconnector' and self._mod(model) in MODELS:
            return False
        return None
