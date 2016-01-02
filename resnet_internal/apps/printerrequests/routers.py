"""
.. module:: resnet_internal.apps.printerrequests.routers
   :synopsis: University Housing Internal Printer Request Database Routers.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""


class PrinterRequestsRouter(object):
    """Routes all printer request models to the correct database."""

    DATABASE_ALIAS = "printers"
    APP_NAME = "printerrequests"

    def db_for_read(self, model, **hints):
        """Routes database read requests to the printer request database."""

        if model._meta.app_label == self.APP_NAME:
            return self.DATABASE_ALIAS
        return None

    def db_for_write(self, model, **hints):
        """Routes database write requests to the printer request database."""

        if model._meta.app_label == self.APP_NAME:
            return self.DATABASE_ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if a printer request model is involved."""

        if obj1._meta.app_label == self.APP_NAME or obj2._meta.app_label == self.APP_NAME:
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """Disallow RMS migrations."""

        if app_label == self.APP_NAME:
            return False
        return None
