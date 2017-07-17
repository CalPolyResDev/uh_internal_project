"""
.. module:: uh_internal.tests.core.test_models
   :synopsis: uh_internal Core Models Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from django.test.testcases import TestCase

from uh_internal.apps.core.models import Community

class CommunityTestCase(TestCase):
    def setUp(self):
        Community.objects.create(name="ResNet")

    def test_communities_address(self):
        resnet = Community.objects.get(name="ResNet")
        self.assertEqual(resnet.address, "ResNet")

