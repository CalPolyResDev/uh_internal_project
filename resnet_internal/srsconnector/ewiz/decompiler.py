from url_builders import Read
from django.db.utils import DatabaseError
from functools import wraps
import sys, urllib2, re

#
# The EnterpriseWizard database backend decompiler
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
# Ewiz results decompiler
#
# Send requests to the EnterpriseWizard database via the REST API and parses the response.
#
class EwizDecompiler():

    def __init__(self, model, settingsDict):
        self.model = model
        self.settingsDict = settingsDict

    #
    # Requests tickets given a query url and parses each result.
    #
    # This method returns a list of field, value dictionaries. Each dictionary represents a ticket.
    #
    @safe_call
    def decompile(self, url):
        count, responseList = self.__request_multiple(url)
        queryList = []

        for response in responseList:
            queryList.append(self.__decompile(response))

        return queryList

    #
    # Requests tickets given a query url and parses only the ticket count.
    #
    # This method returns the number of tickets the given query returned.
    #
    @safe_call
    def count(self, url):
        count, responseList = self.__request_multiple(url, countOnly=True)
        return count

    #
    # Parses a multiple ticket response into a list of responses (one for each ticket) and a count the number of tickets returned.
    #
    # Returns either the list of ticket responses or the count of tickets returned, depending on countOnly's value.
    #
    def __request_multiple(self, url, countOnly=False):
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, message:
            raise self.model.DoesNotExist(self.model._meta.object_name + u' matching query does not exist.\n\t' + str(message))

        pattern = re.compile(r"^EWREST_id_.* = '(?P<value>.*)';$", re.DOTALL)

        idList = []
        for line in iter(lambda: unicode(response.readline().decode('string-escape').strip(), 'ISO-8859-1'), ""):
            try:
                idList.append(pattern.match(line).group('value'))
            except:
                raise DatabaseError("Connection Error. The EnterpriseWizard database might be offline.")

        count = int(idList[0])
        idList = idList[1:]
        responseList = []

        # Return only the count before the heavy lifting if countOnly is True
        if countOnly:
            return count, responseList

        for ticketID in idList:
            responseURL = Read(self.settingsDict, self.model._meta.db_table, ticketID).build()
            responseList.append(self.__request_single(responseURL))

        return count, responseList

    #
    # Generates a response for a single ticket
    #
    def __request_single(self, url):
        request = urllib2.Request(url)

        try:
            return urllib2.urlopen(request)
        except urllib2.HTTPError, message:
            raise self.model.DoesNotExist(self.model._meta.object_name + u' matching query does not exist.\n\t' + unicode(str(message)))

    #
    # Parses a response into a field, value dictionary
    #
    def __decompile(self, response):
        dataList = []
        for line in iter(lambda: unicode(response.readline().decode('string-escape').strip(), 'ISO-8859-1'), ""):
            dataList.append(line)

        pattern = re.compile(r"^EWREST_(?P<key>.*?)='(?P<value>.*)';$", re.DOTALL)

        dataDict = {}
        for data in dataList:
            match = pattern.match(data)
            dataDict[match.group('key')] = match.group('value')

        return dataDict
