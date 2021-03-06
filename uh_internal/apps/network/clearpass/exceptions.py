"""
.. module:: uh_internal.apps.network.clearpass.exceptions
   :synopsis: University Housing Internal Network ClearPass Exceptions

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""


class Error(Exception):
    pass


class APIError(Error):
    """Exception raised when an API request fails."""
    pass


class EndpointLookupError(Error):
    """Exception raised when an endpoint can't be found."""
    pass


class EndpointUpdateError(Error):
    """Exception raised when an endpoint can't be updated."""
    pass


class EndpointUnknownOwnerError(Error):
    """Exception raised when an endpoint's owner can't be found."""
    pass


class EndpointInvalidOperationError(Error):
    """Exception raised when a user attemts to perform an operation that is not
    allowed by ResNet policy."""


class MultipleEndpointError(Error):
    """Exception raised when multiple endpoints are returned
    and 1 was expected."""

    pass
