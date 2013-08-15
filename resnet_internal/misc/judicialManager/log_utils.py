from resnet_internal.judicialManager.models import Logs
from django.utils.encoding import smart_str
import datetime, re
#
# Judicial Management Application Cisco Log Handling Utility
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

#
# Gather possible logs. This will filter out the appropriate logs from the database.
# Makes three filtering passes on the logs:
#        1. incident_datetime
#        2. incident_datetime + 12 hours
#        3. incident datetime + 24 hours
# Logs are filtered by IP Address and then by time from the three time slots.
#
# The result from each pass is then displayed on the screen to be verified by the technician.
# If a result is the same as a previous, only the previous is displayed.
#
# The data is passed back and forth in the form of a complex dictionary.
#
class gather_logs:
    auth_data = {
        'log_id': None,
        'log_datetime': None,
        'log_details': None,
    }

    deauth_data = {
        'log_id': None,
        'log_datetime': None,
        'log_details': None,
    }

    def gather_auth(self, start_date, end_date, ip_address):
        query_set = Logs.objects.using('cisco_logs').all() # The 'using' method tells the model which database to use
        try: # Check if the log exists. If it doesn't, set the data to None
            # Filter the logs, first by type (authentication), then by the passed IP address, and finally by the date range
            gather_pass = query_set.filter(log_details__contains='Authentication:').filter(log_details__contains='Successfully logged in').filter(log_details__contains=ip_address).filter(log_datetime__range=(start_date, end_date))
            gather_pass = gather_pass.latest()
            self.auth_data['log_id'] = int(gather_pass.lid)
            self.auth_data['log_datetime'] = datetime.datetime.strptime(gather_pass.log_datetime, '%Y-%m-%d %H:%M:%S')
            self.auth_data['log_details'] = smart_str(gather_pass.log_details, encoding='utf-8', strings_only=False, errors='strict')
        except Logs.DoesNotExist: # If the log isn't found, set the data to None
            self.auth_data = None

        return self.auth_data

    def gather_deauth(self, start_date, constituent_id, mac_address, ip_address):
        # There are three different log types: SW_Management, Authentication, and Administration
        # As long as the log exists, the overwriting priority is factored by earliest log

        # Administration - Administer kicks constituent to renew lease
        query_set = Logs.objects.using('cisco_logs').all() # The 'using' method tells the model which database to use    
        try: # Check if the log exists. If it doesn't, set the data to None
            # Filter the logs, first by type (SW_Management), then by the passed IP address, and finally by the date range
            gather_pass = query_set.filter(log_details__contains='Administration:').filter(log_details__contains='forcefully logged out by Administrator').filter(log_details__contains=ip_address).filter(log_details__contains=constituent_id).filter(log_details__contains=mac_address).filter(log_datetime__gte=(start_date))[:1].get()
            if gather_pass:
                self.deauth_data['log_id'] = int(gather_pass.lid)
                self.deauth_data['log_datetime'] = datetime.datetime.strptime(gather_pass.log_datetime, '%Y-%m-%d %H:%M:%S')
                self.deauth_data['log_details'] = smart_str(gather_pass.log_details, encoding='utf-8', strings_only=False, errors='strict')
        except Logs.DoesNotExist: # If the log isn't found, set the data to None
            administration_DNE = True

        # Authentication - User logs out
        query_set = Logs.objects.using('cisco_logs').all() # The 'using' method tells the model which database to use    
        try: # Check if the log exists. If it doesn't, set the data to None
            # Filter the logs, first by type (SW_Management), then by the passed IP address, and finally by the date range
            gather_pass = query_set.filter(log_details__contains='Authentication:').filter(log_details__contains='Logged out successfully').filter(log_details__contains=ip_address).filter(log_details__contains=constituent_id).filter(log_details__contains=mac_address).filter(log_datetime__gte=(start_date))[:1].get()
            if gather_pass:
                if administration_DNE or gather_pass.log_datetime < self.deauth_data['log_datetime']:
                    self.deauth_data['log_id'] = int(gather_pass.lid)
                    self.deauth_data['log_datetime'] = datetime.datetime.strptime(gather_pass.log_datetime, '%Y-%m-%d %H:%M:%S')
                    self.deauth_data['log_details'] = smart_str(gather_pass.log_details, encoding='utf-8', strings_only=False, errors='strict')

        except Logs.DoesNotExist: # If the log isn't found, set the data to None
            authentication_DNE = True

        # SW_Management - Switch kicks constituent for inactivity
        query_set = Logs.objects.using('cisco_logs').all() # The 'using' method tells the model which database to use    
        try: # Check if the log exists. If it doesn't, set the data to None
            # Filter the logs, first by type (SW_Management), then by the passed IP address, and finally by the date range
            gather_pass = query_set.filter(log_details__contains='SW\_Management:').filter(log_details__contains='Kicked').filter(log_details__contains=ip_address).filter(log_details__contains=constituent_id).filter(log_details__contains=mac_address).filter(log_datetime__gte=(start_date))[:1].get()
            if gather_pass:
                if (administration_DNE and authentication_DNE) or gather_pass.log_datetime < self.deauth_data['log_datetime']:
                    self.deauth_data['log_id'] = int(gather_pass.lid)
                    self.deauth_data['log_datetime'] = datetime.datetime.strptime(gather_pass.log_datetime, '%Y-%m-%d %H:%M:%S')
                    self.deauth_data['log_details'] = smart_str(gather_pass.log_details, encoding='utf-8', strings_only=False, errors='strict')
        except Logs.DoesNotExist: # If the log isn't found, set the data to None
            pass

        # If a log wasn't found, set the data to None
        if not self.deauth_data['log_id']:
            self.deauth_data = None

        # Return the data
        return self.deauth_data

#
# Parses database information into a dictionary containing the log datetime, constituent ID, IP Address, MAC Address,
# and the log details given raw data.
#
class parse_logs:
    log_data = {
        'first_pass': {
            'auth_log_id': None,
            'auth_log_datetime': None,
            'auth_constituent_id': None,
            'auth_ip_address': None,
            'auth_mac_address': None,
            'auth_log_details': None,
            'deauth_log_id': None,
            'deauth_log_datetime': None,
            'deauth_log_details': None,
        },
        'second_pass': {
            'auth_log_id': None,
            'auth_log_datetime': None,
            'auth_constituent_id': None,
            'auth_ip_address': None,
            'auth_mac_address': None,
            'auth_log_details': None,
            'deauth_log_id': None,
            'deauth_log_datetime': None,
            'deauth_log_details': None,
        },
        'third_pass': {
            'auth_log_id': None,
            'auth_log_datetime': None,
            'auth_constituent_id': None,
            'auth_ip_address': None,
            'auth_mac_address': None,
            'auth_log_details': None,
            'deauth_log_id': None,
            'deauth_log_datetime': None,
            'deauth_log_details': None,
        },
    }

    search_datetime = None

    def __init__(self, search_datetime, ip_address):
        self.search_datetime = search_datetime
        for gather_pass in self.log_data:
            self.log_data[gather_pass]['auth_ip_address'] = ip_address

        self.fetch_auth() # Grab the authentication logs
        self.clean() # Clean up redundant / empty passes
        self.parse_auth() # Parse the authentication records
        self.fetch_deauth() # Grab the deauthentication logs

    def fetch_auth(self):
        # Get the auth data for each pass
        start_date = self.search_datetime - datetime.timedelta(days=14)
        end_date = self.search_datetime

        for fetch_pass in self.log_data:
            ip_address = self.log_data[fetch_pass]['auth_ip_address']
            gatherer = gather_logs()
            try: # Check if a log wasn't found
                gather_pass = gatherer.gather_auth(start_date, end_date, ip_address) # Gather raw data
                self.log_data[fetch_pass]['auth_log_id'] = gather_pass['log_id'] # Set auth log ID
                self.log_data[fetch_pass]['auth_log_datetime'] = gather_pass['log_datetime'] # Set auth log datetime
                self.log_data[fetch_pass]['auth_log_details'] = gather_pass['log_details'] # Set auth log details
            except TypeError:
                self.log_data[fetch_pass] = None
            end_date += datetime.timedelta(hours=12) # Add time for each pass

    def clean(self):
        # Check for duplicates
        try:
            if self.log_data['third_pass']['auth_log_id'] == self.log_data['first_pass']['auth_log_id']:
                self.log_data['third_pass'] = None
        except TypeError:
            pass

        try:
            if self.log_data['third_pass']['auth_log_id'] == self.log_data['second_pass']['auth_log_id']:
                self.log_data['third_pass'] = None
        except TypeError:
            pass

        try:
            if self.log_data['second_pass']['auth_log_id'] == self.log_data['first_pass']['auth_log_id']:
                self.log_data['second_pass'] = None
        except TypeError:
            pass

        try:
            if self.log_data['second_pass']['auth_log_id'] == self.log_data['third_pass']['auth_log_id']:
                self.log_data['second_pass'] = None
        except TypeError:
            pass

        # Clear empty passes (thus also clearing redundant passes)
        if not self.log_data['first_pass']:
            del self.log_data['first_pass']

        if not self.log_data['second_pass']:
            del self.log_data['second_pass']

        if not self.log_data['third_pass']:
            del self.log_data['third_pass']

    def parse_auth(self):
        # Parse each pass
        for gather_pass in self.log_data:
            searchPattern = re.compile(r'^.*Authentication:\s\[(?P<MACAddress>.*?)\s##\s' + self.log_data[gather_pass]['auth_ip_address'] + '\]\s(?P<constituentID>.{0,8})\s-\sSuccessfully logged in')
            try:
                self.log_data[gather_pass]['auth_mac_address'] = searchPattern.match(self.log_data[gather_pass]['auth_log_details']).group('MACAddress') # Grabs the MAC Address
                self.log_data[gather_pass]['auth_constituent_id'] = searchPattern.match(self.log_data[gather_pass]['auth_log_details']).group('constituentID') # Grabs the Resident ID
            except AttributeError:
                print "The log details for the " + gather_pass + " were unable to be parsed."

    def fetch_deauth(self):
        # Get the deauth data for each pass
        for fetch_pass in self.log_data:
            start_date = self.log_data[fetch_pass]['auth_log_datetime']
            constituent_id = self.log_data[fetch_pass]['auth_constituent_id']
            mac_address = self.log_data[fetch_pass]['auth_mac_address']
            ip_address = self.log_data[fetch_pass]['auth_ip_address']
            gatherer = gather_logs()
            try: # Check if a log wasn't found
                gather_pass = gatherer.gather_deauth(start_date, constituent_id, mac_address, ip_address) # Gather raw data
                self.log_data[fetch_pass]['deauth_log_id'] = gather_pass['log_id'] # Set deauth log ID
                self.log_data[fetch_pass]['deauth_log_datetime'] = gather_pass['log_datetime'] # Set deauth log datetime
                self.log_data[fetch_pass]['deauth_log_details'] = gather_pass['log_details'] # Set deauth log details
            except TypeError:
                pass
