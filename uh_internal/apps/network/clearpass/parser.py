"""
.. module:: uh_internal.apps.network.clearpass.parser
   :synopsis: University Housing Internal ClearPass Parser

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from datetime import datetime
import logging
import re

from django.conf import settings

from ..models import ClearPassLoginAttempt
from uh_internal.apps.core.utils import static_vars
from django.db.utils import DataError
from uh_internal.apps.network.utils import validate_mac
from django.core.exceptions import ValidationError


SYSLOG_ENTRY_REGEX = re.compile(r'<[0-9]+>[^,]+,[0-9]+ (?P<clearpass_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) UH User Troubleshooting [0-9]+ [0-9] [0-9] Common\.Username=(?P<username>[^,]+),Common\.Service=(?P<service>[^,]+),Common\.Roles=(?P<roles>.*?),Common\.Host-MAC-Address=(?P<client_mac_address>[0-9a-f]+),(RADIUS\.Acct-Framed-IP-Address=\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3},)?Common\.NAS-IP-Address=\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3},Common\.Request-Timestamp=(?P<timestamp>[^,]+),Common\.Enforcement-Profiles=(?P<enforcement_profiles>.*?),(Common\.Alerts=(?P<alerts>.*?),)*Common\.Login-Status=(?P<login_status>[A-Z]+)')
CLEARPASS_TIMESTAMP_PATTERN = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger(__name__)


def _ensure_email(username):
    if '@' not in username:
        username = username + '@calpoly.edu'
    return username


def _parse_login_result(login_result):
    for number, result_string in ClearPassLoginAttempt.RESULT_CHOICES:
        if result_string == login_result:
            return number

    return None


@static_vars(loginAttempts=[])
def parse_login_attempts(attempts_string):
    for match in SYSLOG_ENTRY_REGEX.finditer(attempts_string):
        attempt_info = match.groupdict()

        if attempt_info['service'] not in settings.CLEARPASS_SERVICE_IGNORE:
            loginAttempt = ClearPassLoginAttempt()
            loginAttempt.username = _ensure_email(attempt_info['username']) if not validate_mac(attempt_info['username']) else None
            loginAttempt.time = datetime.strptime(attempt_info['timestamp'].rsplit('-', 1)[0], CLEARPASS_TIMESTAMP_PATTERN)
            loginAttempt.service = attempt_info['service']
            loginAttempt.roles = attempt_info['roles'].split(', ')
            loginAttempt.client_mac_address = attempt_info['client_mac_address']
            loginAttempt.enforcement_profiles = attempt_info['enforcement_profiles'].split(', ')
            loginAttempt.result = _parse_login_result(attempt_info['login_status'])
            loginAttempt.clearpass_ip = attempt_info['clearpass_ip']
            loginAttempt.alerts = attempt_info['alerts']

            try:
                loginAttempt.clean_fields()
                parse_login_attempts.loginAttempts.append(loginAttempt)
            except ValidationError:
                print('Invalid Attempt: ' + str(loginAttempt))

    if len(parse_login_attempts.loginAttempts) > 50:
        print('Sending')
        try:
            ClearPassLoginAttempt.objects.bulk_create(parse_login_attempts.loginAttempts)
        finally:
            parse_login_attempts.loginAttempts = []
