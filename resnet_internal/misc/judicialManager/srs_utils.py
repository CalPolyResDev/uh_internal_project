import re, datetime

#
# Judicial Management Application SRS Ticket Handling Utility
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

#
# Captures and/or parses SRS ticket data.
#
class parse_ticket:
    ticket_data = {
            'ticket_number': None,
            'referrer_name': None,
            'referrer_datetime': None,
            'incident_ip': None,
            'incident_datetime': None,
            'incident_details': None,
            'used_bittorrent': None,
        }

    def __init__(self, ticket_number):
        self.ticket_data['ticket_number'] = ticket_number
        self.get_ticket_info()
        self.parse_incident_details()

    def get_ticket_info(self):
        # Connect to the SRS database
        self.ticket_data['referrer_name'] = None # referrer name
        self.ticket_data['referrer_datetime'] = datetime.datetime.strptime(None, "%b %d %Y %H:%M:%S") # when the ticket was sent to ResNet
        self.ticket_data['incident_ip'] = None # ip adddress
        self.ticket_data['incident_datetime'] = datetime.datetime.strptime(None, "%b %d %Y %H:%M:%S") # incident date/time

    def parse_incident_details(self):
        # Grab the full incident details from the ticket
        self.ticket_data['incident_details'] = None

        # Split the data twice to get the incident details section
        splitA = re.split('#*\s?Infringement\s?Details\s?#*', self.ticket_data['incident_details'])[1]
        splitB = re.split('#*', splitA)[0]

        # Set the parsed incident details
        self.ticket_data['incident_details'] = splitB

        # Check if BitTorrent was used
        stripped = re.sub(r'\s', '', splitB) # Strip whitespace
        lowercase = stripped.lower() # Convert to lowercase
        searchPattern = re.compile(r'.*protocol:bittorrent')
        try: # Check if the BitTorrent string exists
            searchPattern.match(lowercase).groups()
            self.ticket_data['used_bittorrent'] = True
        except AttributeError:
            self.ticket_data['used_bittorrent'] = False

#
# Commit data to an SRS Confidential Ticket
#
def set_log_data(self, ticket_number, log_data, work_log):
    # Handle the constituent ID
    sub_username = log_data['auth_constituent_id'] # Set the sub username to the constituent id. See if it has the capability to auto-populate with the SRS API
    summary = None
    summary = log_data['auth_constituent_id'] + " - " + summary # Add the constituent ID to the beginning of the summary

    # Handle the MAC Address
    MAC_Address = log_data['auth_mac_address'] # Set the MAC Address

    # Add the work log
    work_log = work_log

#
# Set the blocked date in an SRS Confidential Ticket
#
def set_blocked_date(self, ticket_number):
    blocked = True
    blocked_date = datetime.datetime.strftime("%b %d %Y %H:%M:%S", datetime.datetime.now()) # Not sure how the datetime needs to be sent

#
# Set the unblocked date in an SRS Confidential Ticket
#
def set_unblocked_date(self, ticket_number):
    unblocked = True
    unblocked_date = datetime.datetime.strftime("%b %d %Y %H:%M:%S", datetime.datetime.now()) # Not sure how the datetime needs to be sent

#
# Change the status ofan SRS Confidential Ticket
#
def change_status(self, ticket_number, status):
    status = status
