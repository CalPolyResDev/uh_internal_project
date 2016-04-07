"""
.. module:: uh_internal.apps.network.airwaves.exceptions
   :synopsis: University Housing Internal Airwaves Connector Exceptions

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""


class Error(Exception):
    pass


class ClientLookupError(Error):
    """Exception raised when a client can't be found."""
    pass
