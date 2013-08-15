"""
.. module:: rmsconnector.models
   :synopsis: RMS Connector Models.

   RMS model relationships are extremely sensitive.
   DO NOT ATTEMPT TO MODIFY DATABASE RELATIONSHIPS IN ANY FAHSION.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import re

from django.db.models import CharField, DateField, DecimalField, TextField, IntegerField, ForeignKey, Model, Manager

from .managers import BuildingManager, CommunityManager


class StudentProfile(Model):
    """ RMS Student Profile.

    This table holds student information about a resident.
    The "rms_id" field has a foreign key relationship with the "ResidentProfile" model.

    """

    rms_id = ForeignKey('ResidentProfile', primary_key=True, db_column='pk_rms_id')
    empl_id = CharField(max_length=20, blank=True, db_column='ix_student_number')
    ethnicity = CharField(max_length=25, db_column='fk_ethnicity')
    nationality = CharField(max_length=25, db_column='fk_nationality')  # Domestic: 'NA'
    student_type = CharField(max_length=5, db_column='fk_student_type')
    college = CharField(max_length=30, db_column='fk_school')
    major = CharField(max_length=30, db_column='fk_major')
    current_gpa = CharField(max_length=15, blank=True, db_column='gpa')
    course_year = CharField(max_length=15, blank=True)
    school_attended = CharField(max_length=30, blank=True)
    nonstud_department = CharField(max_length=50, blank=True)
    nonstud_university_status = CharField(max_length=50)
    medical_conditions = CharField(max_length=50, blank=True, db_column='medical')
    insurance_preference_1 = CharField(max_length=50, blank=True, db_column='preference1')
    insurance_preference_2 = CharField(max_length=50, blank=True, db_column='preference2')
    notes = TextField(blank=True, db_column='student_profile_comment')

    def __unicode__(self):
        return self.rms_id.full_name

    class Meta:
        db_table = u'pple_t_student_profile'
        managed = False
        verbose_name = u'RMS Student Profile'


class StudentAddress(Model):
    """ RMS Student Address.

    This table holds information on a resident's permanent address (off-campus address).
    The "rms_id" field has a foreign key relationship with the "ResidentProfile" model. It is NOT unique.

    """

    rms_id = ForeignKey('ResidentProfile', primary_key=True, db_column='ck_rms_id')
    email = CharField(max_length=50, blank=True, db_column='e_mail')
    phone = CharField(max_length=25, blank=True, db_column='location_phone')
    address_type = CharField(primary_key=True, max_length=15, db_column='ck_address_type')
    address_line_1 = CharField(max_length=50, blank=True, db_column='address_1')
    address_line_2 = CharField(max_length=50, blank=True, db_column='address_1b')
    city = CharField(max_length=50, blank=True, db_column='address_2')
    state = CharField(max_length=8, db_column='fk_state')
    zip_code = CharField(max_length=15, blank=True, db_column='postcode')
    country = CharField(max_length=50, blank=True, db_column='address_3')

    def __get_alias(self):
        """ Parses a Cal Poly alias from the email field.

        :returns: The residents's Cal Poly alias.

        """

        try:
            return self.email.split('@calpoly.edu')[0]
        except AttributeError:
            return None
    alias = property(__get_alias)

    def __unicode__(self):
        return self.alias

    class Meta:
        db_table = u'pple_t_address'
        managed = False
        verbose_name = u'RMS Student Address'


class ResidentProfile(Model):
    """ RMS Resident Profile.

    This table holds general information about a resident. It holds no student information.
    The rms_id in this model IS unique.

    """

    rms_id = IntegerField(primary_key=True, db_column='pk_rms_id')
    person_type = CharField(max_length=4)
    birth_date = DateField(null=True, blank=True)
    sex = CharField(max_length=1, blank=True)
    title = CharField(max_length=5, blank=True)
    first_name = CharField(max_length=25, db_column='ix_first_name')
    middle_name = CharField(max_length=25, blank=True, db_column='ix_middle_name')
    last_name = CharField(max_length=25, db_column='ix_last_name')
    phone_work = CharField(max_length=25, blank=True)
    phone_cell = CharField(max_length=25, blank=True)
    fax = CharField(max_length=25, blank=True)
    password = CharField(max_length=250, blank=True)
    second_password = CharField(max_length=250, blank=True)
    allow_web_access = IntegerField()
    mailing = IntegerField()
    stud_screen_name = CharField(max_length=250, blank=True)
    fk_category_id = IntegerField(null=True, blank=True)
    notes = TextField(blank=True)

    def __get_full_name(self):
        """ Builds a full name from the first_name and last_name fields.

        :returns: The residents's full name.

        """

        return self.first_name + " " + self.last_name
    full_name = property(__get_full_name)

    def __get_formatted_cell(self):
        """ Removes non-numeric characters from the phone_cell field.

        :returns: The resident's cell phone number, only digits

        """

        return re.sub("\D", "", self.phone_cell)
    formatted_cell = property(__get_formatted_cell)

    def __unicode__(self):
        return self.full_name

    class Meta:
        db_table = u'pple_t_person'
        managed = False
        verbose_name = u'RMS Resident Profile'


class RoomBookings(Model):
    """ RMS Room Bookings.

    This table holds information on a student's room (on-campus address).
    The "rms_id" and "term_id" fields have foreign key relationships with the "ResidentProfile" (NOT Unique)
    and "TermDates" models, respectively.

    """

    rms_id = ForeignKey('ResidentProfile', db_column='ck_rms_id')
    bed_space = ForeignKey('Room', primary_key=True, db_column='ck_bed_space')
    check_in = DateField(null=True, blank=True)
    check_out = DateField(null=True, blank=True)
    move_in_date = DateField(unique=True, db_column='ck_move_in_date')
    move_out_date = DateField(null=True, blank=True, db_column='room_person_move_out_date')
    turn_around_date = DateField(null=True, blank=True)
    order_id = IntegerField(unique=True, db_column='fk_order_id')
    room_order_id = CharField(unique=True, max_length=20, db_column='sk_room_order_id')
    application_type = CharField(max_length=50, blank=True)
    booking_type = CharField(max_length=5, blank=True, db_column='room_person_booking_type')
    booking_hold = IntegerField(null=True, blank=True)
    booked_by = CharField(max_length=30, blank=True, db_column='room_person_booked_by')
    rate = DecimalField(max_digits=18, decimal_places=5, db_column='room_person_rate')
    rate_code = CharField(max_length=10, db_column='fk_rate_code')
    rate_config_no = IntegerField(null=True, blank=True, db_column='fk_rate_config_no')
    billing_type = CharField(max_length=50, db_column='fk_billing_type')
    billed_up_to = DateField(null=True, blank=True, db_column='room_person_billed_up_to')
    term_id = ForeignKey('TermDates', blank=True, db_column='fk_term_id')
    swsa_details = CharField(max_length=250, blank=True)
    notes = CharField(max_length=250, blank=True, db_column='room_person_notes')

    def __unicode__(self):
        return self.bed_space_id

    class Meta:
        db_table = u'rmgt_t_room_person'
        managed = False
        verbose_name = u'RMS Room Booking'


class RoomConfigs(Model):
    """ RMS Room Configuration.

    This table holds information on a student's room configuration.
    The "bed_space" and "section" fields have foreign key relationships with
    the "RoomBookings" and "FloorSections" models, respectively.

    """

    bed_space = ForeignKey('Room', unique=True, primary_key=True, db_column='ck_bed_space')
    room_address = CharField(max_length=50, blank=True, db_column='rooms_address_1')
    floor_section = ForeignKey('FloorSection', db_column='fk_section_id')
    phone_extension = CharField(max_length=16, blank=True)
    capacity = IntegerField(db_column='rooms_capacity')
    gender = CharField(max_length=1)
    room_type = CharField(max_length=15, unique=True, db_column='fk_rooms_type')
    operating_mode = CharField(max_length=1)
    key_id = CharField(max_length=20, blank=True)
    date_opened = DateField(db_column='rooms_start_date')
    status = IntegerField()
    desirability = IntegerField()

    def __unicode__(self):
        return self.bed_space_id

    class Meta:
        db_table = u'rmgt_t_room_configs'
        managed = False
        verbose_name = u'RMS Room Configuration'


class Room(Model):
    """ RMS Room.

    This table holds information on a university housing room.

    """

    bed_space = CharField(max_length=10, unique=True, primary_key=True, db_column='pk_bed_space')
    room_no = CharField(max_length=10, db_column='fk_room_no')
    status = IntegerField(null=True, blank=True)

    def __get_formatted_room(self):
        """ Removes unnecessary characters from the room_no field.

        :returns: The resident's room number.

        """

        return self.room_no.split('-')[-1:][0]
    formatted_room = property(__get_formatted_room)

    def __unicode__(self):
        return self.formatted_room

    class Meta:
        db_table = u'rmgt_t_rooms'
        managed = False
        verbose_name = u'RMS Room'


class FloorSection(Model):
    """ RMS Floor Section.

    This table holds information on a university housing floor section.
    The "floor" field has a foreign key relationship with the "Floor" model.

    """

    section_id = CharField(max_length=8, unique=True, primary_key=True, db_column='pk_section_id')
    name = CharField(max_length=50, db_column='floor_sections_name')
    floor = ForeignKey('Floor', db_column='fk_floor_id')
    status = IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'rmgt_t_floor_sections'
        managed = False
        verbose_name = u'RMS Floor Section'


class Floor(Model):
    """ RMS Floor.

    This table holds information on a university housing floor.
    The "building" field has a foreign key relationship with the "Building" model.

    """

    floor_id = CharField(max_length=8, unique=True, primary_key=True, db_column='pk_floor_id')
    name = CharField(max_length=50, db_column='floors_name')
    building = ForeignKey('Building', db_column='fk_building_id')
    status = IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'rmgt_t_floors'
        managed = False
        verbose_name = u'RMS Floor'


class Building(Model):
    """ RMS Building.

    This table holds information on a university housing building.
    The "community" field has a foreign key relationship with the "Community" model.

    """

    building_id = CharField(max_length=8, unique=True, primary_key=True, db_column='pk_building_id')
    name = CharField(max_length=30, db_column='buildings_name')
    community = ForeignKey('Community', db_column='fk_community')
    address_street = CharField(max_length=50, blank=True, db_column='buildings_address_1')
    address_building = CharField(max_length=50, blank=True, db_column='buildings_address_1b')
    address_city = CharField(max_length=50, blank=True, db_column='buildings_address_2')
    address_zip_code = CharField(max_length=15, blank=True, db_column='buildings_postcode')
    address_state = CharField(max_length=15, blank=True, db_column='buildings_state')
    status = IntegerField()

    objects = BuildingManager()
    raw_objects = Manager()

    def __get_formatted_name(self):
        """ Correctly converts the buidling's name to a format usable by this application.

        :returns: The name of the resident's building.

        """

        if self.name == "Cerro Vista":
            return u'San Luis'
        else:
            return self.name.replace(self.community_id, "").replace(" Hall", "").replace(" Tower ", "Tower_")
    formatted_name = property(__get_formatted_name)

    def __get_full_address(self):
        """ Combines all address fields into one.

        :returns: The address of the resident's building.

        """

        return self.address_street + " " + self.address_building + ", " + self.address_city + ", " + self.address_state + " " + self.address_zip_code
    full_address = property(__get_full_address)

    def __unicode__(self):
        return self.formatted_name

    class Meta:
        db_table = u'rmgt_t_buildings'
        managed = False
        verbose_name = u'RMS Building'


class Community(Model):
    """ RMS Community.

    This table holds information on a university housing community.

    """

    community = CharField(max_length=25, unique=True, primary_key=True, db_column='pk_community')
    status = IntegerField()

    objects = CommunityManager()
    raw_objects = Manager()

    def __unicode__(self):
        return self.community

    class Meta:
        db_table = u'rmgt_t_community'
        managed = False
        verbose_name = u'RMS Community'


class BuckleyFlag(Model):
    """ RMS Buckley Flag.

    This table holds a resident's incident information.

    The model has been configured for the sole purpose of determining buckley status.

    """

    rms_id = ForeignKey("ResidentProfile", db_column='ck_rms_id')
    buckley_flag_id = ForeignKey("BuckleyFlagID", unique=True, primary_key=True, db_column='ck_incident_id')

    def __get_buckley_status(self):
        """ Retrieves the residents buckley status.

        :returns: True if the resident has buckley status, false otherwise

        """

        return self.buckley_flag_id_id == 42
    is_buckley = property(__get_buckley_status)

    class Meta:
        db_table = u'inct_t_incident_person'
        managed = False
        verbose_name = u'RMS Buckley Flag'


class BuckleyFlagID(Model):
    """ RMS Buckley Flag ID.

    This table holds a buckley flag ID.

    """

    buckley_id = IntegerField(primary_key=True, db_column='pk_incident_id')

    class Meta:
        db_table = u'inct_t_incidents'
        managed = False
        verbose_name = u'RMS Buckley Flag ID'


class TermDates(Model):
    """ RMS Term Dates

    This table holds information on the current term.

    """

    term_id = CharField(primary_key=True, max_length=8, db_column='pk_term_id')
    name = CharField(max_length=25, blank=True, db_column='term_dates_name')
    start_date = DateField(db_column='term_dates_start_date')
    end_date = DateField(db_column='term_dates_end_date')
    status = IntegerField()
    room_term = IntegerField(null=True, blank=True)
    plan_term = IntegerField(null=True, blank=True)
    billing_term = IntegerField(null=True, blank=True)
    property_term = IntegerField(null=True, blank=True)
    payment_term = IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'rmgt_t_term_dates'
        managed = False
        verbose_name = u'RMS Term Date'
