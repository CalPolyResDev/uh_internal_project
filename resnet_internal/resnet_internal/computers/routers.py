"""
.. module:: resnet_internal.computers.routers
   :synopsis: ResNet Internal Computer Index Database Routers.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""


class ComputersRouter(object):
    """ A Django database router that ensures the computers models use the computers database

    This router must be added to the 'DATABASE_ROUTERS' list in the project
    settings.

    This router supports all operations.

    """

    ALIAS = "computers"
    APP_NAME = "computers"

    def _app(self, model):
        """ A shortcut to retrieve the provided model's application label.

        :param model: A model instance from which to retrieve information.
        :type model: model
        :returns: The provided model's app label.

        """

        return model._meta.app_label

    def _mod(self, model):
        """ A shortcut to retrieve the provided model's module name, a lower-cased version of its object name.

        :param model: A model instance from which to retrieve information.
        :type model: model
        :returns: The provided model's module name.

        """

        return model._meta.module_name

    def db_for_read(self, model, **hints):
        """Routes database read requests to the correct database."""

        if self._app(model) == self.APP_NAME:
            return self.ALIAS
        return None

    def db_for_write(self, model, **hints):
        """Routes database read requests to the correct database."""

        if self._app(model) == self.APP_NAME:
            return self.ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Provides no constraints on relationships."""

        return None

    def allow_syncdb(self, db, model):
        """Provides no constraints on table synchronization."""

        return None
