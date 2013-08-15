from django.conf import settings
import imaplib, email, re

#
# Judicial Management Application Email Handling Utility
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#
# NOTE: Email settings are pulled from the settings file
#

#
# Email Checker - Update the application's Judicial database
#
# First, this checks ResNet's email inbox for judicials when a technician loads the manager using the python IMAP library.
# The ticket number is then parsed from the subject line and added to a list of ticket numbers.
# That list is then cross-checked with our judicial database (both active and archived tables).
# If the judicial does not already exist, an open ticket will created and put into the judicial database.
#
class check_email:
    ticket_list = []

    def __init__(self):
        # Create ticket list
        self.ticket_list = self.get_ticket_list()

    def get_ticket_list(self):
        ticket_numbers = []
        server = None

        # Connect to the server and authenticate
        if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
            server = imaplib.IMAP4_SSL(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
        else:
            server = imaplib.IMAP4(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
        server.login(settings.INCOMING_EMAIL['IMAP4']['USER'], settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])

        # Grab the ticket number
        server.select('inbox', readonly=True) # Select the Inbox
        r, search_data = server.search(None, "(SUBJECT CP#)") # Narrow the results by searching for subjects containing CP#
        for num in search_data[0].split():
            r, message_data = server.fetch(num, '(RFC822)') # Fetch the messages with that subject
            for response_part in message_data:
                if isinstance(response_part, tuple):
                    message = email.message_from_string(response_part[1])
                    # Parse the ticket number from the email subject
                    subject = (message['subject'])
                    ticketPattern = re.compile(r'CP#(?P<ticketNumber>.*?)-Re:')
                    ticket = re.sub(r'\s', '', subject)
                    # Add the ticket numbers to the list
                    try:
                        ticket_numbers.append(int(ticketPattern.match(ticket).groups()[0]))
                    except:
                        pass
        server.logout() # Disconnect from the server
        return ticket_numbers # Returns a list of ticket numbers currently in the inbox

    def cross_check_records(self, ticket_list):
        for ticket in ticket_list:
            # Check database records
            # for record in Judicials:
            if True:
                return None

    def create_judicial(self, ticket_number):
        return None

#
# Moves the email for the passed ticket number to the 'Abuse Complaints' folder
#
def move_to_abuse(self, ticket_number):
    server = None

    # Connect to the server and authenticate
    if settings.INCOMING_EMAIL['IMAP4']['USE_SSL']:
        server = imaplib.IMAP4_SSL(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
    else:
        server = imaplib.IMAP4(settings.INCOMING_EMAIL['IMAP4']['HOST'], settings.INCOMING_EMAIL['IMAP4']['PORT'])
    server.login(settings.INCOMING_EMAIL['IMAP4']['USER'], settings.INCOMING_EMAIL['IMAP4']['PASSWORD'])

    # Grab the ticket number
    server.select('inbox', readonly=False) # Select the Inbox
    r, search_data = server.search(None, '(SUBJECT ' + ticket_number + ')') # Narrow the results by searching for subjects containing CP#
    for num in search_data[0].split():
        r, message_data = server.fetch(num, '(RFC822)') # Fetch the messages with that subject
        for response_part in message_data:
            if isinstance(response_part, tuple):
                message = email.message_from_string(response_part[1])
                # Parse the ticket number from the email subject
                subject = (message['subject'])
                ticketPattern = re.compile(r'CP#(?P<ticketNumber>.*?)-Re:')
                ticket = re.sub(r'\s', '', subject)
                # Check if the email exists. If it does, move it to the abuse folder.
                try:
                    ticketPattern.match(ticket).groups()
                    r, uid_data = server.fetch(num, "(UID)") # Fetch the UID
                    uidPattern = re.compile('\d+ \(UID (?P<uid>\d+)\)')
                    uid = uidPattern.match(uid_data[0]).group('uid')
                    r = server.uid('COPY', uid, 'Abuse Complaints') # Copy the email to the abuse folder
                    if r[0] == 'OK':
                        r, message_data = server.uid('STORE', uid , '+FLAGS', '(\Deleted)') # Commit the copy and mark the email as deleted
                except AttributeError:
                    pass
    server.expunge() # Clear all emails marked as deleted
    server.logout() # Disconnect from the server
