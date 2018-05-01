"""
.. module:: uh_internal.core.tests
   :synopsis: uh_internal Core Tests.
.. moduleauthor:: Kyle Reis (@kjreis)
"""

from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError
from django.test import TestCase

from .models import Community, Building, Room, Department, SubDepartment, ADGroup

class CommunityTestCases(TestCase):
    """ Tests the Community model from models.py """

    def setUp(self):
        Community.objects.create(name="ResNet")

    def test_community_str(self):
        """ Tests the Community __str__ function """

        community = Community.objects.get(name="ResNet")
        self.assertEqual(str(community), "ResNet")

    def test_communities_address(self):
        """ Tests the Community address property """

        community = Community.objects.get(name="ResNet")
        self.assertEqual(community.address, "ResNet")

    def test_bad_community_name(self):
        """ Tests a bad Community name """

        # a 31 character name
        name31 = "testing1234567890testing1234567"

        with self.assertRaises(DataError):
            Community.objects.create(name=name31)


class BuildingTestCases(TestCase):
    """ Tests the Building model from models.py """

    def setUp(self):
        self.community = Community.objects.create(name="ResNet")
        Building.objects.create(name="office", community=self.community)

    def test_building_str(self):
        """ Tests the Building __str__ function """

        building = Building.objects.get(name="office")
        self.assertEqual(str(building), "office")

    def test_building_address(self):
        """ Tests the Building address property """

        building = Building.objects.get(name="office")
        self.assertEqual(building.address, "ResNet office")

    def test_bad_building_name(self):
        """ Tests a bad Building name """

        # a 31 character name
        name31 = "testing1234567890testing1234567"

        with self.assertRaises(DataError):
            Building.objects.create(name=name31, community=self.community)

    def test_no_community(self):
        """ Tests not having an associated Community """

        with self.assertRaises(IntegrityError):
            Building.objects.create(name="Test")

class RoomTestCases(TestCase):
    """ Tests the Room model from models.py """

    def setUp(self):
        self.community = Community.objects.create(name="ResNet")
        self.building = Building.objects.create(name="office", community=self.community)
        # Note that the save function converts the name to uppercase
        Room.objects.create(name="main", building=self.building)

    def test_room_str(self):
        """ Tests the Room __str__ function """

        room = Room.objects.get(name="MAIN")
        self.assertEqual(str(room), "MAIN")

    def test_room_community(self):
        """ Tests the Room community property """

        room = Room.objects.get(name="MAIN")
        self.assertEqual(room.community, self.community)

    def test_room_address(self):
        """ Tests the Room address property """

        room = Room.objects.get(name="MAIN")
        self.assertEqual(room.address, "ResNet office MAIN")

    def test_bad_room_name(self):
        """ Tests a bad Room name """

        # a 31 character name
        name31 = "testing1234567890testing1234567"

        with self.assertRaises(DataError):
            Room.objects.create(name=name31, building=self.building)

    def test_no_building(self):
        """ Tests not having an associated Building """

        with self.assertRaises(IntegrityError):
            Building.objects.create(name="Test")


class DepartmentTestCases(TestCase):
    """ Tests the Department model from models.py """

    def setUp(self):
        Department.objects.create(name="ResNet")

    def test_department_str(self):
        """ Tests the Department __str__ function """

        department = Department.objects.get(name="ResNet")
        self.assertEqual(str(department), "ResNet")

    def test_bad_department_name(self):
        """ Tests a bad Department name """

        # a 51 character name
        name51 = "testing1234567890testing1234567890testing1234567890"

        with self.assertRaises(DataError):
            Department.objects.create(name=name51)


class SubDepartmentTestCases(TestCase):
    """ Tests the SubDepartment model from models.py """

    def setUp(self):
        dept = Department.objects.create(name="ResNet")
        SubDepartment.objects.create(name="dev", department=dept)

    def test_department_str(self):
        """ Tests the SubDepartment __str__ function """

        subdepartment = SubDepartment.objects.get(name="dev")
        self.assertEqual(str(subdepartment), "dev")

    def test_bad_department_name(self):
        """ Tests a bad SubDepartment name """

        # a 51 character name
        name51 = "testing1234567890testing1234567890testing1234567890"

        with self.assertRaises(DataError):
            SubDepartment.objects.create(name=name51)


class ADGroupTestCases(TestCase):
    """ Tests the ADGroup model from models.py """

    def setUp(self):
        # I'm not sure why this works, the validator should throw an error (I think)
        ADGroup.objects.create(distinguished_name="test", display_name="test")

    def test_adgroup_str(self):
        """ Tests the ADGroup __str__ function """

        adgroup = ADGroup.objects.get(distinguished_name="test")
        self.assertEqual(str(adgroup), "test")

    def test_bad_adgroup_name(self):
        """ Tests a bad ADGroup name """

        # a 51 character name
        name51 = "testing1234567890testing1234567890testing1234567890"

        with self.assertRaises(DataError):
            ADGroup.objects.create(distinguished_name=(name51 * 5))
            ADGroup.objects.create(display_name=name51)
