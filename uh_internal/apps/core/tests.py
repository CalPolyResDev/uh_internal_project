"""
.. module:: uh_internal.core.tests
   :synopsis: uh_internal Core Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from django.test import TestCase

from .models import Community, Building

class CommunityTestCase(TestCase):
    """ Tests the Community model from models.py """

    def setUp(self):
        Community.objects.create(name="ResNet")

    def test_community_str(self):
        """ Tests the Community __str__ function """

        resnet = Community.objects.get(name="ResNet")
        self.assertEqual(str(resnet), "ResNet")

    def test_communities_address(self):
        """ Tests the Community address property """

        resnet = Community.objects.get(name="ResNet")
        self.assertEqual(resnet.address, "ResNet")


class BuildingTestCase(TestCase):
    """ Tests the Building model from models.py """

    def setUp(self):
        community = Community.objects.create(name="ResNet")
        Building.objects.create(name="office", community=community)

    def test_building_str(self):
        """ Tests the Building __str__ function """

        resnet = Building.objects.get(name="office")
        self.assertEqual(str(resnet), "office")

    def test_building_address(self):
        """ Tests the Building address property """

        resnet = Building.objects.get(name="office")
        self.assertEqual(resnet.address, "ResNet office")
