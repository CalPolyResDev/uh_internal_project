"""
.. module:: uh_internal.uploaders.test_ajax
   :synopsis: uh_internal Uploaders AJAX Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from datetime import datetime
from django.test.testcases import TestCase
from django.http import HttpRequest

from .models import Uploaders
from .ajax import log_uploader

class UploadersAJAXTestCase(TestCase):
    """def test_log_uploader_success(self):
        request = HttpRequest()
        request._body = {"uploader": "test2",
                         "success": True}
        log_uploader(request)
        uploader = Uploaders.objects.get(name="test2")
        self.assertEqual(str(uploader), "test2 Uploaded on " + str(datetime.now()))

    def test_log_uploader_fail(self):
        request = HttpRequest()
        request._body = {"uploader": "test",
                         "success": False}
        log_uploader(request)
        uploader = Uploaders.objects.get(name="test")
        self.assertEqual(str(uploader), "test Failed on " + str(datetime.now()))"""
