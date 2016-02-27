"""
.. module:: resnet_internal.apps.orientation.middleware
   :synopsis: University Housing Internal Orientation Middleware.

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy


class OrientationRedirectMiddleware(object):

    def process_request(self, request):
        if 'orientation' not in request.path and 'flugzeug' not in request.path:
            if request.user.is_authenticated() and (not request.user.orientation_complete and request.user.orientation_access):
                return HttpResponseRedirect(reverse_lazy('orientation_checklist'))

        return None
