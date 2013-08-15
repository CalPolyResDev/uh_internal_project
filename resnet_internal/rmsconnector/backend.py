"""
.. module:: rmsconnector.backend
   :synopsis: RMS Connector Authentication Backend.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from .utils import Resident


class RMSBackend(object):
    """Authenticates users against the RMS database using a cal poly alias and date of birth."""

    def authenticate(self, alias=None, dob=None):
        # Make sure the paramaters are valid types
        if not (type(alias) is str or type(alias) is unicode):
            raise AttributeError("Error RMSBackend: Alias (alias) must be <type 'str'> or <type 'unicode'>, found %s" % type(alias))
        elif type(dob) is not datetime.date:
            raise AttributeError("Error RMSBackend: Date of birth (dob) must be <type 'datetime.date'>, found %s" % type(dob))

        # See if the user exists in the rms database (alias is valid)
        try:
            resident = Resident(alias)
        except ObjectDoesNotExist:
            return None

        currentTimeDelta = dob - resident.get_birth_date()
        dob_valid = (currentTimeDelta.total_seconds() == 0)

        if dob_valid:
            try:
                django_user = User.objects.get(username=alias)
            except User.DoesNotExist:
                # Create a new user.
                django_user = User(username=alias)
                django_user.set_unusable_password()
                django_user.first_name = resident.get_full_name().split(" ")[0]
                django_user.last_name = resident.get_full_name().split(" ")[-1]
                django_user.email = resident.get_email()
                django_user.is_staff = False
                django_user.is_superuser = False
                django_user.save()
            return django_user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
