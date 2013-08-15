from resnet_internal.judicialManager import email_utils, log_utils, srs_utils, doc_utils
from django.contrib.auth.models.User import get_full_name
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
#
# Judicial Management Application Views
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

# Update the Judicials database and then open the active tickets page of the Judicial Manager
def juicial_manager():
    # Update the application's judicial database
    update_judicials = email_utils.check_email()

    return render_to_response('judicialManager/active.html')

def judicial_archive():
    return None

def csd_home(request):
    return render_to_response('judicialManager/csd.html', locals(), context_instance=RequestContext(request))

def move_to_archive(ticket_number):
    # move the ticket from the active database into the archive database
    return None

def process_ticket(ticket_number):
    data_container = judicial_data(ticket_number)



#
# A class to gather and process judicial data.
#
class judicial_data:
    process_init_datetime = None
    verifier = get_full_name() # The full name of the technician that initiated this judicial process
    ticket_data = None
    raw_log_data = None # Full log data, multiple passes
    log_data = None # Narrowed log data, single pass

    # Initiate the data  
    def __init__(self, ticket_number):
        # Capture process start time
        self.process_init_datetime = datetime.datetime.strftime("%A, %B %d, %Y %I:%M:%S %p", datetime.datetime.now()) # Monday, January 01, 2012 12:00:00 AM

        # Capture ticket data
        ticket_parser = srs_utils.parse_ticket(ticket_number)
        self.ticket_data = ticket_parser.ticket_data

        # Capture full log data. This data still contains separate passes.
        log_parser = log_utils.parse_logs(self.ticket_data['incident_datetime'], self.ticket_data['incident_ip'])
        self.raw_log_data = log_parser.log_data
