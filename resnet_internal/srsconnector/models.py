"""
.. module:: srsconnector.models
    :synopsis: SRS Connector Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models import Model, AutoField, CharField, TextField, IntegerField

from .fields import ListField, DictField, EwizDateTimeField, YNBooleanField, YesNoBooleanField

DATABASE_ALIAS = "common"


class StaffMapping(Model):
    """A mapping of various department staff to their respective positions."""

    staff_title = CharField(max_length=35, unique=True, verbose_name=u'Staff Title')
    staff_name = CharField(max_length=50, verbose_name=u'Staff Full Name')
    staff_alias = CharField(max_length=8, verbose_name=u'Staff Alias')
    staff_ext = IntegerField(max_length=4, verbose_name=u'Staff Telephone Extension')

    class Meta:
        db_table = u'staffmapping'
        managed = False
        verbose_name = u'Campus Staff Mapping'


class PrinterRequest(Model):
    """A service request ticket for toner and part replacement requests."""

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Work In Progress', 'Work In Progress'),
        ('Closed', 'Closed')
    ]
    PRIORITY_CHOICES = [
        ('Low', 'Low'),  # Not crucial or important; respond as time permits
        ('Medium', 'Medium'),  # Standard problem, question, or request; standard response time acceptable
        ('High', 'High'),  # Important work cannot be completed until ticket is resolved; respond as quickly as possible
        ('Urgent', 'Urgent')  # Time critical work cannot be completed until ticket is resolved. Urgent problems or requests should also be called i
    ]
    CONTACT_CHOICES = [
        ('Choose One', 'Choose One'),
        ('Email', 'Email'),
        ('Phone', 'Phone'),
        ('Other', 'Other')
    ]
    PRINTER_MODEL_CHOICES = [
        ('5100cn', '5100cn'),
        ('5110cn', '5110cn'),
        ('5130cdn', '5130cdn')
    ]
    PRINTER_MANUFACTURER_CHOICES = [
        ('Dell', 'Dell')
    ]
    REQUEST_TYPE_CHOICES = [
        ('**TONER_REQUEST', 'TONER'),
        ('**PARTS_REQUEST', 'PARTS')
    ]

    ticket_id = AutoField(primary_key=True, db_column='id')
    status = CharField(max_length=25, choices=STATUS_CHOICES, default='Open', db_column='wfstate')
    priority = CharField(max_length=25, choices=PRIORITY_CHOICES, default='Low')
    assigned_team = CharField(help_text=':', max_length=50, editable=False, default='SA RESNET', db_column='team_name')

    requestor_username = CharField(help_text=':', max_length=25, db_column='submitter_username')
    requestor_full_name = CharField(max_length=50, editable=False, db_column='full_name')
    requestor_building = CharField(max_length=50, editable=False, db_column='building')
    requestor_room = CharField(max_length=15, editable=False, db_column='room')
    requestor_phone = CharField(max_length=15, editable=False, db_column='direct_phone')
    contact_method = CharField(max_length=15, choices=CONTACT_CHOICES, default='Email', db_column='preferred_contact_method')
    preferred_contact_times = DictField()

    general_issue = CharField(max_length=50, default='Hardware Problem')
    specific_issue = CharField(max_length=50, default='Printer Issue')

    printer_model = CharField(max_length=15, choices=PRINTER_MODEL_CHOICES, db_column='model')
    printer_manufacturer = CharField(max_length=15, choices=PRINTER_MANUFACTURER_CHOICES, db_column='manufacturer')
    printer_property_id = CharField(max_length=50, blank=True, db_column='cal_poly_property_id')

    request_type = CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, db_column='summary')
    request_list = ListField(db_column='problem_description')  # Either a list of toner colors or a list of parts
    work_log = TextField(blank=True, db_column='staff_only_notes')  # Name and Timestamp are automatically added by Ewiz
    solution = TextField(blank=True)

    class Meta:
        db_table = u'helpdesk_case'
        managed = False
        verbose_name = u'Printer Request'

    def __get_email(self):
        """Return the submitter's email."""

        try:
            return self.submitterUsername + u'@calpoly.edu'
        except AttributeError:
            return None
    submitterEmail = property(__get_email)


class AccountRequest(Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Work In Progress', 'Work In Progress'),
        ('Closed', 'Closed')
    ]
    REQUEST_TYPES = [
        ('New Account', 'Add'),
        ('Account Modification', 'Remove'),
    ]
    ACTION_DESCRIPTION_CHOICES = [
        ('Please add to ResNet team. Signed RUP form is attached.', 'Add'),
        ('Please remove from ResNet team.', 'Remove'),
    ]

    srs_account_manager = StaffMapping.objects.using(DATABASE_ALIAS).get(staff_title="ITS: SRS Account Manager").staff_name
    assistant_resident_coordinator = StaffMapping.objects.using(DATABASE_ALIAS).get(staff_title="ResNet: Assistant Resident Coordinator").staff_alias

    ticket_id = AutoField(primary_key=True, db_column='id')
    status = CharField(max_length=25, choices=STATUS_CHOICES, default='Open', db_column='wfstate')
    assigned_person = CharField(help_text=':', max_length=50, default=srs_account_manager)
    assigned_team = CharField(help_text=':', max_length=50, default='ITS Service Desk')

    requestor_username = CharField(help_text=':', max_length=25, default=assistant_resident_coordinator, db_column='req_username')
    subject_username = CharField(help_text=':', max_length=25)

    request_type = CharField(max_length=50, choices=REQUEST_TYPES, default='New Account')
    request_subtype = CharField(max_length=50, default='Resnet Technician')

    action = CharField(max_length=75, choices=ACTION_DESCRIPTION_CHOICES, default='Please add to ResNet team. Signed RUP form is attached.', db_column='description')

    # Use this field only in conjunction with EwizAttacher - do not attempt to populate it
    file_field = TextField(help_text='file', editable=False, db_column='attached_files')

    class Meta:
        db_table = u'account_request'
        managed = False
        verbose_name = u'Account Request'


class ServiceRequest(Model):
    """This is a list of all currently known model fields in the helpdesk_case table."""

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Work In Progress', 'Work In Progress'),
        ('Closed', 'Closed')
    ]
    PRIORITY_CHOICES = [
        ('Low', 'Low'),  # Not crucial or important; respond as time permits
        ('Medium', 'Medium'),  # Standard problem, question, or request; standard response time acceptable
        ('High', 'High'),  # Important work cannot be completed until ticket is resolved; respond as quickly as possible
        ('Urgent', 'Urgent')  # Time critical work cannot be completed until ticket is resolved. Urgent problems or requests should also be called in to the IS service desk
    ]
    CONTACT_CHOICES = [
        ('Email', 'Email'),
        ('Phone', 'Phone'),
        ('Other', 'Other')
    ]

    ticket_id = AutoField(primary_key=True, db_column='id')
    ticket_type = CharField(max_length=25, db_column='type')
    status = CharField(max_length=25, choices=STATUS_CHOICES, default='Open', db_column='wfstate')
    priority = CharField(max_length=25, default='Low')
    created_by = CharField(max_length=50, editable=False)
    creator_username = CharField(max_length=25, editable=False)
    date_created = EwizDateTimeField(editable=False)
    assigned_team = CharField(help_text=':', max_length=50, db_column='team_name')
    assigned_person = CharField(help_text=':', max_length=50)
    assigned_team_leader = CharField(max_length=50, editable=False, db_column='team_leader')
    override_default_team = YesNoBooleanField(db_column='override_default_team')

    requestor_username = CharField(help_text=':', max_length=25, db_column='submitter_username')
    requestor_full_name = CharField(max_length=50, editable=False, db_column='full_name')
    requestor_role = CharField(max_length=50, editable=False, db_column='primary_role')
    requestor_housing_address = CharField(max_length=75, editable=False, db_column='univ_housing_address')
    requestor_housing_phone = CharField(max_length=15, editable=False, db_column='univ_housing_phone')
    requestor_building = CharField(max_length=50, editable=False, db_column='building')
    requestor_room = CharField(max_length=15, editable=False, db_column='room')
    requestor_department = CharField(max_length=50, editable=False, db_column='dept_description')
    requestor_phone = CharField(max_length=15, editable=False, db_column='direct_phone')
    contact_method = CharField(max_length=15, choices=CONTACT_CHOICES, default='Email', db_column='preferred_contact_method')
    preferred_contact_times = DictField()
    is_student = YNBooleanField(editable=False, db_column='student_flag')
    is_ferpa = YNBooleanField(editable=False, db_column='ferpa_flag')

    general_issue = CharField(max_length=50)
    specific_issue = CharField(max_length=50)
    issue_type = CharField(max_length=50, default='End User Issue', db_column='type_of_problem')

    lab_lelated = YesNoBooleanField(db_column='does_this_relate_to_a_lab')
    residence_hall_related = YesNoBooleanField(db_column='reshall_related')

    model = CharField(max_length=50)
    manufacturer = CharField(max_length=50)
    property_id = CharField(max_length=50, blank=True, db_column='cal_poly_property_id')

    summary = CharField(max_length=250)
    description = TextField(db_column='problem_description')
    work_log = TextField(blank=True, db_column='staff_only_notes')  # Name and Timestamp are automatically added by Ewiz
    latest_log = TextField(editable=False, db_column='latest_notes_appended')
    requestor_notification = TextField(blank=True, db_column='additional_information')  # Name and Timestamp are automatically added by Ewiz
    solution = TextField(blank=True)

    updated_by = CharField(max_length=50, editable=False)
    updater_username = CharField(max_length=25, editable=False)
    updater_is_technician = YNBooleanField(editable=False, db_column='updater_technician_staff_flag')
    date_updated = EwizDateTimeField(editable=False)

    times_reopened = IntegerField(editable=False, db_column='number_of_times_reopened')
    reopen = YesNoBooleanField(db_column='i_would_like_to_reopen_this_request')

    last_escalated = EwizDateTimeField(editable=False, null=True, db_column='escalation_date')
    times_escalated = IntegerField(editable=False, db_column='number_of_times_escalated')

    class Meta:
        db_table = u'helpdesk_case'
        managed = False
        verbose_name = u'General Service Request'
