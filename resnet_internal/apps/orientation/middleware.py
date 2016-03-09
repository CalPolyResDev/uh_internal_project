"""
.. module:: resnet_internal.apps.orientation.middleware
   :synopsis: University Housing Internal Orientation Middleware.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from ...settings.base import ORIENTATION_ACCESS


class OrientationRedirectMiddleware(object):

    def process_request(self, request):
        if 'orientation' not in request.path and 'flugzeug' not in request.path:
            if request.user.is_authenticated() and (not request.user.orientation_complete and request.user.has_access(ORIENTATION_ACCESS)):
                return HttpResponseRedirect(reverse_lazy('orientation:home'))

        return None
