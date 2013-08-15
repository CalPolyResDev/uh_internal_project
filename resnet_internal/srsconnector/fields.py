from django.core.exceptions import ValidationError
from django.db.models import SubfieldBase, DateTimeField, TextField, BooleanField
import ast, datetime

#
# Special Ewiz and Non-Relational Model Fields
#
# Author: Alex Kavanaugh
# Email: kavanaugh.development@outlook.com
#
# ListField and DictField derived from ListField, which was written by stackoverflow.com/users/194311/jathanism.
#

class EwizDateTimeField(DateTimeField):
    __metaclass__ = SubfieldBase
    description = "Stores a dateTime with Ewiz standards."

    error_messages = {
        'invalid': "'%s' value has an invalid format. It must be in Mmm DD YYYY HH:MM:SS format.",
        'invalid_date': "'%s' value has the correct format (Mmm DD YYYY) but it is an invalid date.",
        'invalid_datetime': "'%s' value has the correct format (Mmm DD YYYY HH:MM:SS) but it is an invalid date/time.",
    }

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            value = datetime.datetime(value.year, value.month, value.day)
            return value

        try:
            parsed = datetime.datetime.strptime(value, "%b %d %Y %H:%M:%S")
            if parsed is not None:
                return parsed
        except ValueError:
            msg = self.error_messages['invalid_datetime'] % value
            raise ValidationError(msg)

        try:
            parsed = datetime.datetime.strptime(value, "%b %d %Y")
            if parsed is not None:
                return datetime.datetime(parsed.year, parsed.month, parsed.day)
        except ValueError:
            msg = self.error_messages['invalid_date'] % value
            raise ValidationError(msg)

        msg = self.error_messages['invalid'] % value
        raise ValidationError(msg)

    def get_prep_value(self, value):
        value = self.to_python(value)
        return value

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return '' if val is None else val.isoformat()

class YNBooleanField(BooleanField):

    __metaclass__ = SubfieldBase
    description = "Stores a Y/N boolean value"

    def __init__(self, *args, **kwargs):
        super(YNBooleanField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in (True, False):
            # if value is 1 or 0 than it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if value == u'Y':
            return True
        if value == u'N':
            return False
        msg = self.error_messages['invalid'] % value
        raise ValidationError(msg)

    def get_prep_value(self, value):
        if value is None:
            return None
        if value:
            return u'Y'
        else:
            return u'N'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class YesNoBooleanField(BooleanField):

    __metaclass__ = SubfieldBase
    description = "Stores a Yes/No boolean value"

    def __init__(self, *args, **kwargs):
        super(YesNoBooleanField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in (True, False):
            # if value is 1 or 0 than it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if value == u'Yes':
            return True
        if value == u'No':
            return False
        msg = self.error_messages['invalid'] % value
        raise ValidationError(msg)

    def get_prep_value(self, value):
        if value is None:
            return None
        if value:
            return u'Yes'
        else:
            return u'No'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class ListField(TextField):
    __metaclass__ = SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        try:
            return ast.literal_eval(value)
        except:
            return []

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class DictField(TextField):
    __metaclass__ = SubfieldBase
    description = "Stores a python dict"

    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = {}

        if isinstance(value, dict):
            return value

        try:
            return ast.literal_eval(value)
        except:
            return {}

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
