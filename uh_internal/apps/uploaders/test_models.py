"""
.. module:: uh_internal.uploaders.test_models
   :synopsis: uh_internal Uploaders Models Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from django.test.testcases import TestCase
from datetime import datetime

from .models import Uploaders

class UploadersTestCase(TestCase):
    def setUp(self):
        Uploaders.objects.create(name="test",
                                 last_run=datetime(2018, 4, 27, 8, 20),
                                 successful=True)
        Uploaders.objects.create(name="test2",
                                 last_run=datetime(2018, 4, 27, 8, 20),
                                 successful=False)

    def test_uploader_success_str(self):
        uploader = Uploaders.objects.get(name="test")
        self.assertEqual(str(uploader), "test Uploaded on " + str(datetime(2018, 4, 27, 8, 20)))

    def test_uploader_fail_str(self):
        uploader = Uploaders.objects.get(name="test2")
        self.assertEqual(str(uploader), "test2 Failed on " + str(datetime(2018, 4, 27, 8, 20)))
