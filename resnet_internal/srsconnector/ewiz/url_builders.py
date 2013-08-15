from django.db.utils import DatabaseError
from functools import wraps
import sys, urllib

#
# The EnterpriseWizard REST url builders
#
# Author: Alex Kavanaugh
# Email: kavanaugh.development@outlook.com
#

#
# Function wrapper for debugging - taken from Django-Nonrel/djangotoolbox
#
def safe_call(func):
    @wraps(func)
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            raise DatabaseError, DatabaseError(*tuple(e)), sys.exc_info()[2]
    return _func

#
# Builds a READ url
#
# Sending a READ request returns a response containing fields and values for the provided ticket ID
#
class Read():

    def __init__(self, settingsDict, table, ticketID):
        if settingsDict["PORT"] == "443":
            self.protocol = u'https://'
        else:
            self.protocol = u'http://'

        self.host = settingsDict["HOST"]
        self.knowledgeBase = settingsDict["NAME"]
        self.login = settingsDict["USER"]
        self.password = settingsDict["PASSWORD"]
        self.language = u'en'
        self.table = table
        self.ticketID = ticketID

    @safe_call
    def build(self):
        return urllib.quote(self.protocol + self.host + u'EWRead?$KB=' + self.knowledgeBase + u'&$table=' + self.table + u'&$login=' + self.login + u'&$password=' + self.password + u'&$lang=' + self.language + u'&id=' + str(self.ticketID), ":/?$&='")

#
# Builds a Select url
#
# Sending a SELECT request returns a response containing the number of tickets and a list of ticketIDs that adhere to the query constraints.
#
class Select():

    def __init__(self, settingsDict, table, compiledQuery):
        if settingsDict["PORT"] == "443":
            self.protocol = u'https://'
        else:
            self.protocol = u'http://'

        self.host = settingsDict["HOST"]
        self.knowledgeBase = settingsDict["NAME"]
        self.login = settingsDict["USER"]
        self.password = settingsDict["PASSWORD"]
        self.language = u'en'
        self.table = table
        self.compiledQuery = compiledQuery

    @safe_call
    def build(self):
        return urllib.quote(self.__build_select() + self.__build_where(), ":/?$&='")

    def __build_select(self):
        return self.protocol + self.host + u'EWSelect?$KB=' + self.knowledgeBase + u'&$table=' + self.table + u'&$login=' + self.login + u'&$password=' + self.password + u'&$lang=' + self.language

    def __build_where(self):
        # Build filters string
        filters = u''
        for queryFilter in self.compiledQuery["filters"][:-1]:
            filters += queryFilter + u' AND '
        else:
            filters += self.compiledQuery["filters"][-1]

        # Build ordering string
        ordering = u' ORDER BY '
        for order in self.compiledQuery["ordering"][:-1]:
            ordering += order + u', '
        else:
            ordering += self.compiledQuery["ordering"][-1]

        # Build limits string
        limit = u' LIMIT ' + self.compiledQuery["limits"]["limit"]
        offset = u' OFFSET ' + self.compiledQuery["limits"]["offset"]

        return u'&where=' + filters + ordering + limit + offset

#
# Builds an Insert url
#
# Assuming there are no errors in the request, sending an INSERT request creates a ticket
# in the EnterpriseWizard database and returns the automatically generated ticketID.
#
class Insert():

    def __init__(self, settingsDict, table, data):
        if settingsDict["PORT"] == "443":
            self.protocol = u'https://'
        else:
            self.protocol = u'http://'

        self.host = settingsDict["HOST"]
        self.knowledgeBase = settingsDict["NAME"]
        self.login = settingsDict["USER"]
        self.password = settingsDict["PASSWORD"]
        self.language = u'en'
        self.table = table
        self.data = data

    @safe_call
    def build(self):
        return urllib.quote(self.__build_insert() + self.__build_data() + u'&time_spent=0:0:1:0', ":/?$&='")

    @safe_call
    def __build_insert(self):
        return self.protocol + self.host + u'EWCreate?$KB=' + self.knowledgeBase + u'&$table=' + self.table + u'&$login=' + self.login + u'&$password=' + self.password + u'&$lang=' + self.language

    @safe_call
    def __build_data(self):
        dataString = u''
        for field, value in self.data:
            # Only insert if the field is editable and the field has a value or is allowed to be blank
            if (value or field.blank):  # field.editable and
                dataString += u'&' + field.column + u'=' + field.help_text + unicode(str(value))

        return dataString

#
# Builds an Update url
#
# Assuming there are no errors in the request, sending an UPDATE request updates/changes data
# in a ticket in the EnterpriseWizard database. Nothing is returned.
#
class Update():

    def __init__(self, settingsDict, table, ticketID, data):
        if settingsDict["PORT"] == "443":
            self.protocol = u'https://'
        else:
            self.protocol = u'http://'

        self.host = settingsDict["HOST"]
        self.knowledgeBase = settingsDict["NAME"]
        self.login = settingsDict["USER"]
        self.password = settingsDict["PASSWORD"]
        self.language = u'en'
        self.table = table
        self.ticketID = unicode(str(ticketID))
        self.data = data

    @safe_call
    def build(self):
        return urllib.quote(self.__build_update() + self.__build_data() + u'&time_spent=0:0:1:0', ":/?$&='")

    @safe_call
    def __build_update(self):
        return self.protocol + self.host + u'EWUpdate?$KB=' + self.knowledgeBase + u'&$table=' + self.table + u'&$login=' + self.login + u'&$password=' + self.password + u'&$lang=' + self.language

    @safe_call
    def __build_data(self):
        dataString = u'&id=' + self.ticketID
        for field, value in self.data:
            # Only update if the field is editable and the field has a value or is allowed to be blank
            if field.editable and (value or field.blank):
                dataString += u'&' + field.column + u'=' + field.help_text + unicode(str(value))

        return dataString

#
# Builds an ATTACH url
#
# The ATTACH request must be sent via HTTP PUT. The number of attached files is returned upon upload success.
#
class Attach():

    def __init__(self, settingsDict, table, ticketID, fieldName, fileName):
        if settingsDict["PORT"] == "443":
            self.protocol = u'https://'
        else:
            self.protocol = u'http://'

        self.host = settingsDict["HOST"]
        self.knowledgeBase = settingsDict["NAME"]
        self.login = settingsDict["USER"]
        self.password = settingsDict["PASSWORD"]
        self.language = u'en'
        self.table = table
        self.ticketID = ticketID
        self.fieldName = fieldName
        self.fileName = fileName

    @safe_call
    def build(self):
        return urllib.quote(self.protocol + self.host + u'EWAttach?$KB=' + self.knowledgeBase + u'&$table=' + self.table + u'&$login=' + self.login + u'&$password=' + self.password + u'&$lang=' + self.language + u'&id=' + str(self.ticketID) + u'&field=' + str(self.fieldName) + u'&fileName=' + str(self.fileName), ":/?$&='")
