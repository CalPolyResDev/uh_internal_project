"""
.. module:: uh_internal.uploaders.tests
   :synopsis: uh_internal Uploaders Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from datetime import datetime
from django.db import DataError, IntegrityError
from django.test import TestCase, RequestFactory

from .models import Uploaders
from .ajax import log_uploader

class UploadersTestCase(TestCase):
    """ Tests the functionality of models.py """

    def setUp(self):
        Uploaders.objects.create(name="test",
                                 last_run=datetime(2018, 4, 27, 8, 20),
                                 successful=True)
        Uploaders.objects.create(name="test2",
                                 last_run=datetime(2018, 4, 27, 8, 20),
                                 successful=False)

    def test_uploader_success_str(self):
        """ Tests a successful uploads print string """

        uploader = Uploaders.objects.get(name="test")
        self.assertEqual(str(uploader), "test Uploaded on " + str(datetime(2018, 4, 27, 8, 20)))

    def test_uploader_fail_str(self):
        """ Tests a failed uploads print string """

        uploader = Uploaders.objects.get(name="test2")
        self.assertEqual(str(uploader), "test2 Failed on " + str(datetime(2018, 4, 27, 8, 20)))

    def test_bad_uploader_name(self):
        """ Tests a bad uploader name """

        with self.assertRaises(DataError):
            Uploaders.objects.create(name="testing1234567890")


class UploadersAJAXTestCase(TestCase):
    """ Tests the functionality of ajax.py """

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        # Regex expression for valid datetime string
        self.dtregex = r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).(\d{6}))"

    def test_log_uploader_success(self):
        """ Tests if a successful upload is logged correctly """

        body = {"uploader": "test2",
                "success": True}
        request = self.factory.post('/uploaders/log_upload/', body)
        response = log_uploader(request)
        self.assertEqual(response.status_code, 200)
        uploader = Uploaders.objects.get(name="test2")
        self.assertRegex(str(uploader), "(test2 Uploaded on " + self.dtregex)

    def test_log_uploader_fail(self):
        """ Tests if a failed upload is logged correctly """

        body = {"uploader": "test",
                "success": False}
        request = self.factory.post('/uploaders/log_upload/', body)
        response = log_uploader(request)
        self.assertEqual(response.status_code, 200)
        uploader = Uploaders.objects.get(name="test")
        self.assertRegex(str(uploader), "(test Failed on " + self.dtregex)

    def test_log_uploader_bad_request(self):
        """ Tests if a bad request throws an error correctly """

        body = {"uploader": "test2"}
        body2 = {"success": False}
        request = self.factory.post('/uploaders/log_upload/', body)
        request2 = self.factory.post('/uploaders/log_upload/', body2)

        with self.assertRaises(KeyError):
            log_uploader(request)
            log_uploader(request2)
