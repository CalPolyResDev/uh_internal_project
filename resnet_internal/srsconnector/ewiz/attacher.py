from url_builders import Attach
import urllib2

#
# The EnterpriseWizard REST file attacher
#
# Author: Alex Kavanaugh
# Email: kavanaugh.development@outlook.com
#

#
# Uploads an attachment to the EnterpriseWizard database.
#
class EwizAttacher():

    def __init__(self, settingsDict, model, filePointer, fileName):
        self.settingsDict = settingsDict
        self.table = model._meta.db_table
        self.ticketID = model.ticketID
        self.file = filePointer
        self.fileName = fileName

        for field in model._meta.fields:
            if field.help_text == 'file':
                self.fieldName = field.column

        if not self.fieldName:
            raise model.DoesNotExist("The file field for this model does not exist.")

    def buildURL(self):
        self.url = Attach(self.settingsDict, self.table, self.ticketID, self.fieldName, self.fileName).build()

    def attachFile(self):
        self.buildURL()

        request = urllib2.Request(self.url, self.file.read(), {'Content-Type': 'application/octet-stream'})
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request)

        # Close the file stream
        self.file.close()

        return response
