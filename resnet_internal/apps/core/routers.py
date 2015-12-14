"""
.. module:: resnet_internal.apps.core.routers
   :synopsis: ResNet Internal Core Database Routers.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""


class CommonRouter(object):
    """
    Routes all common models to the correct database.

    Credit for _app and _mod methods: Kyle Dodson <kdodson@caloply.edu>
    """

    ALIAS = "common"
    APP_NAME = "core"
    MODELS = ['staffmapping', 'printertype', 'toner', 'part', 'request', 'request_toner', 'request_parts']  # HERE BE DRAGONS... This takes care of all unmigratable tables

    def _app(self, model):
        """ A shortcut to retrieve the provided model's application label.

        :param model: A model instance from which to retrieve information.
        :type model: model
        :returns: The provided model's app label.

        """

        return model._meta.app_label

    def _mod(self, model):
        """ A shortcut to retrieve the provided model's name, a lower-cased version of its object name.

        :param model: A model instance from which to retrieve information.
        :type model: model
        :returns: The provided model's name.

        """

        return model._meta.model_name

    def db_for_read(self, model, **hints):
        """Routes database read requests to the database only if the requested model belongs to a model in this application's MODELS list."""

        if self._app(model) == self.APP_NAME and self._mod(model) in self.MODELS:
            return self.ALIAS
        return None

    def db_for_write(self, model, **hints):
        """Routes database write requests to the database only if the requested model belongs to a model in this application's MODELS list."""

        if self._app(model) == self.APP_NAME and self._mod(model) in self.MODELS:
            return self.ALIAS
        return None

    # HERE BE DRAGONS... This takes care of all unmigratable tables
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Provides no constraints on table synchronization."""

        if model_name in self.MODELS:
            return False

        if app_label in ["rmsconnector", "srsconnector"]:
            return False

        if str(db) in ["default"]:
            return True
        else:
            return False
