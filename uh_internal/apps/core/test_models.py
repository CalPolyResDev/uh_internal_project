"""
.. module:: uh_internal.core.test_models
   :synopsis: uh_internal Core Models Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from django.test.testcases import TestCase

from .models import Community, Building

class CommunityTestCase(TestCase):
    def setUp(self):
        Community.objects.create(name="ResNet")

    def test_community_str(self):
        resnet = Community.objects.get(name="ResNet")
        self.assertEqual(str(resnet), "ResNet")

    def test_communities_address(self):
        resnet = Community.objects.get(name="ResNet")
        self.assertEqual(resnet.address, "ResNet")


class BuildingTestCase(TestCase):
    def setUp(self):
        community = Community.objects.create(name="ResNet")
        Building.objects.create(name="office", community=community)

    def test_building_str(self):
        resnet = Building.objects.get(name="office")
        self.assertEquals(str(resnet), "office")

    def test_building_address(self):
        resnet = Building.objects.get(name="office")
        self.assertEquals(resnet.address, "ResNet office")
