"""
.. module:: rmsconnector.utils
   :synopsis: RMS Connector Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from datetime import date

from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.db.models import Q

from .models import TermDates, BuckleyFlag, StudentAddress, ResidentProfile, RoomBookings, Room, RoomConfigs


def get_current_term():
    """Returns the current term code."""

    today = date.today()
    terms = []
    for term in TermDates.objects.filter(start_date__lte=today, end_date__gte=today):
        terms.append(term.term_id)
    return terms[0][:4]


def reverse_address_lookup(community="", building="", room=""):
    """ Retrieve a list of RMS IDs corresponding to the passed address parameters. The 'does_not_exist' instance variable is set when a resident with the provided information does not exist.

    :param community: The community by which to filter results.
    :type community: str
    :param building: The building by which to filter results.
    :type building: str
    :param room: The room by which to filter results.
    :type room: str
    :returns: A list of RMS IDs
    :raises: **ObjectDoesNotExist** if no matches can be found using the provided address filters.

    """

    # Convert tower notation back to RMS style
    building = building.replace("_", " ")

    # Build a complex filter
    kwargz = {
        "floor_section__floor__building__community__community__icontains": community,
        "floor_section__floor__building__name__icontains": building,
        "bed_space__bed_space__icontains": room,
    }
    q = Q(**kwargz)

    rooms = RoomConfigs.objects.filter(q)

    residents = []
    for room in rooms:
        residents.extend(RoomBookings.objects.filter(bed_space_id=room.bed_space_id, term_id__term_id__icontains=get_current_term(), check_out=None, check_in__gt='1970-01-01'))

    rmsIDList = []
    for resident in residents:
        rmsIDList.append(resident.rms_id_id)

    if len(rmsIDList) == 0:
        raise ObjectDoesNotExist("The reverse address lookup returned zero results.")
    else:
        return rmsIDList


class Resident:
    """Retrieves and contains resident information."""

    rms_id = None
    alias = None
    full_name = None
    birth_date = None
    email = None
    phone_numbers = None
    address = None
    is_buckley = None
    term_type = None
    does_not_exist = False
    term_code = None
    room_booking_instance = None

    def __init__(self, rms_id=None, alias=None, term_code=None):
        """ Set the resident's RMS ID or retrieve it using a provided Cal Poly Alias.

        :param rms_id: optional. The resident's RMS ID.
        :type rms_id: int
        :param alias: optional. The resident's Cal Poly Alias (used to find RMS ID).
        :type alias: str
        :param term_code: optional. The term code to set for housing lookups.
        :type term_code: int
        :raises: **ObjectDoesNotExist** if no matches can be found using the provided alias.
        :raises: **ImproperlyConfigured** if one of the two parameters is not supplied.

        """

        if not rms_id:
            if alias:
                self.alias = alias
                self.email = alias + '@calpoly.edu'

                try:
                    self.rms_id = StudentAddress.objects.get(email=self.email).rms_id_id
                except StudentAddress.DoesNotExist:
                    self.does_not_exist = True
                    raise ObjectDoesNotExist("An RMS ID could not be found for the resident with Cal Poly alias: '%s'" % self.alias)
            else:
                raise ImproperlyConfigured("The ResidentInfo Class must be instantiated with either an RMS ID or a Cal Poly Alias. Neither was supplied.")
        else:
            self.alias = alias
            self.rms_id = rms_id

        self.term_code = term_code

    def get_rms_id(self):
        """Retrieves the resident's RMS ID.

        :returns: The resident's RMS ID.

        """

        return self.rms_id

    def get_alias(self):
        """ Retreives the resident's Cal Poly Alias.

        :returns: The resident's Cal Poly Alias.
        :raises: **ObjectDoesNotExist** if no matches can be found using the provided information.

        """

        if not self.alias:
            try:
                self.alias = StudentAddress.objects.filter(rms_id_id=self.rms_id).exclude(email="")[0].alias
            except IndexError:
                self.does_not_exist = True
                raise ObjectDoesNotExist("An alias could not be found for the resident with RMS ID: %d" % self.rms_id)

        return self.alias

    def get_full_name(self):
        """ Retrieves the resident's first and last names.

        :returns: The resident's full name.
        :raises: **ObjectDoesNotExist** if no matches can be found using the provided information.

        """
        if not self.full_name:
            try:
                self.full_name = ResidentProfile.objects.get(rms_id=self.rms_id).full_name
            except ResidentProfile.DoesNotExist:
                self.does_not_exist = True
                raise ObjectDoesNotExist("A full name could not be found for the resident with RMS ID: %d" % self.rms_id)

        return self.full_name

    def get_birth_date(self):
        """ Retrieves the resident's birth date.

        :returns: the resident's birth date.
        :raises: **ObjectDoesNotExist** if no matches can be found using the provided information.

        """

        if not self.birth_date:
            try:
                self.full_name = ResidentProfile.objects.get(rms_id=self.rms_id).birth_date
            except ResidentProfile.DoesNotExist:
                self.does_not_exist = True
                raise ObjectDoesNotExist("A birth date could not be found for the resident with RMS ID: %d" % self.rms_id)

        return self.birth_date

    def get_email(self):
        """ Retreives the resident's Cal Poly email address.

        :returns: The resident's Cal Poly email address.
        :raises: **ObjectDoesNotExist** if no matches can be found using the provided information (inherited from get_alias).

        """

        if not self.email:
            if not self.alias:
                self.get_alias()

            self.email = self.alias + '@calpoly.edu'

        return self.email

    def _get_room_bookings_instance(self):
        """ Sets an instance of the resident's room booking.

        :raises: **ObjectDoesNotExist** if a room booking does not exist for the resident.

        """

        try:
            self.room_booking_instance = RoomBookings.objects.get(rms_id_id=self.rms_id, term_id__term_id__icontains=self.term_code, check_out=None, check_in__gt='1970-01-01')
        except RoomBookings.DoesNotExist:
            self.does_not_exist = True
            raise ObjectDoesNotExist("A room booking could not be found for the resident with RMS ID: %d." % self.rms_id)

    def get_phone_numbers(self):
        """ Retrieves the resident's dorm and cell phone numbers.

        :returns: A two-item dictionary containing the resident's dorm and cell phone numbers. If a cell phone number cannot be found, None is returned in it's place.
        :raises: **ObjectDoesNotExist** if a dorm phone number cannot be found or a room booking does not exist for the resident (inherited from _get_room_bookings_instance)

        """

        if not self.phone_numbers:
            if not self.term_code:
                self.term_code = get_current_term()

            if not self.room_booking_instance:
                self._get_room_bookings_instance()

            try:
                bed_space = self.room_booking_instance.bed_space_id
                cell = ResidentProfile.objects.get(rms_id=self.rms_id).formatted_cell
                dorm = RoomConfigs.objects.get(bed_space_id=bed_space).phone_extension

                self.phone_numbers = {"cell": cell, "dorm": dorm}
            except RoomConfigs.DoesNotExist:
                self.does_not_exist = True
                raise ObjectDoesNotExist("A dorm phone number could not be found for the resident with RMS ID: %d." % self.rms_id)

        return self.phone_numbers

    def get_address(self):
        """ Retrieves the resident's address.

        :returns: A three-item dictionary containing the resident's community, building, and room.
        :raises: **ObjectDoesNotExist** if a room booking does not exist for the resident (inherited from _get_room_bookings_instance)

        """

        if not self.address:
            if not self.term_code:
                self.term_code = get_current_term()

            if not self.room_booking_instance:
                self._get_room_bookings_instance()

            try:
                bed_space = self.room_booking_instance.bed_space_id
                roomConfig = RoomConfigs.objects.get(bed_space=bed_space)
                room = Room.objects.get(bed_space=bed_space).formatted_room
                bed = bed_space.split('-')[-1:][0].replace(room, "")
                building = roomConfig.floor_section.floor.building.formatted_name
                community = roomConfig.floor_section.floor.building.community_id
            except RoomBookings.DoesNotExist:
                raise ObjectDoesNotExist("An address could not be found for the resident with RMS ID: %d." % self.rms_id)

            if community == 'Poly Canyon Village' or community == 'Cerro Vista':
                room = room + bed

            self.address = {'community': community, 'building': building, 'room': room}

        return self.address

    def is_buckley(self):
        """ Retrieves a resident's buckley status.

        :returns: True if the resident is buckley, False if he/she is not buckley or does not exist.

        """

        try:
            return BuckleyFlag.objects.get(rms_id=self.rms_id).is_buckley
        except BuckleyFlag.DoesNotExist:
            self.does_not_exist = True
            return False

    def get_term_type(self):
        """ Retrieves a residnet's term type (Continuing, Transfer, or Freshman).

        :returns: The resident's term type.
        :raises: **ObjectDoesNotExist** if a room booking does not exist for the resident (inherited from _get_room_bookings_instance)

        """

        if not self.term_type:
            if not self.term_code:
                self.term_code = get_current_term()

            if not self.room_booking_instance:
                self._get_room_bookings_instance()

            try:
                term_type = self.room_booking_instance.term_id_id[-2:]

                if term_type == 'CO':
                    self.term_type = 'Continuing'
                elif term_type == 'FR':
                    self.term_type = 'Freshman'
                elif term_type == 'CT':
                    self.term_type = 'Transfer'
            except RoomBookings.DoesNotExist:
                raise ObjectDoesNotExist("A term type could not be found for the resident with RMS ID: %d." % self.rms_id)

        return self.term_type
