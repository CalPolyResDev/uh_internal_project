from urllib.parse import quote, urlencode
from ...settings.base import get_env_variable
import base64
import json
import uuid
import time
import requests
from django_ajax.decorators import ajax


graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Client ID and secret
client_id = get_env_variable('UH_INTERNAL_MICROSOFT_APPLICATION_ID')
client_secret = get_env_variable('UH_INTERNAL_MICROSOFT_APPLICATION_SECRET')

# Constant strings for OAuth2 flow
# The OAuth authority
authority = 'https://login.microsoftonline.com'

# The authorize URL that initiates the OAuth2 client credential flow for admin consent
authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
#token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')
token_url = "https://login.microsoftonline.com/cpslo.onmicrosoft.com/oauth2/token"

# Admin consent endpoint
permisssions_url = '{0}{1}'.format(authority, '/common/adminconsent?')

def get_token():
    # Build the post form for the token request
    post_data = { 'grant_type': 'client_credentials',
                'resource': "https://graph.microsoft.com",
                'client_id': client_id,
                'client_secret': client_secret,
                }

    r = requests.post(token_url, data=post_data)

    try:
        return r.json()['access_token']
    except:
        'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

# Get admin consent
def request_permissions():
    get_data = {'client_id': client_id,
                '&state': '12345',
                '&redirect_uri': 'https://internal.housing.calpoly.edu/'
    }

    r = requests.get(permisssions_url, params=get_data)

    try:
        print('requesting permisssions')
        print(r.url)
        return r.url
    except:
        'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

# For Outlook service
# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
    # Send these headers with all API calls
    headers = { 'User-Agent' : 'uh-internal',
              'Authorization' : 'Bearer {0}'.format(token),
              'Accept' : 'application/json',
              'X-AnchorMailbox' : user_email }

    # Use these headers to instrument calls. Makes it easier
    # to correlate requests and responses in case of problems
    # and is a recommended best practice.
    request_id = str(uuid.uuid4())
    instrumentation = { 'client-request-id' : request_id,
                      'return-client-request-id' : 'true' }

    headers.update(instrumentation)

    response = None

    if (method.upper() == 'GET'):
        response = requests.get(url, headers = headers, params = parameters)
    elif (method.upper() == 'DELETE'):
        response = requests.delete(url, headers = headers, params = parameters)
    elif (method.upper() == 'PATCH'):
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
    elif (method.upper() == 'POST'):
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

    return response

def get_me(access_token):
    get_me_url = graph_endpoint.format('/me')

    # Use OData query parameters to control the results
    #  - Only return the displayName and mail fields
    query_parameters = {'$select': 'displayName,mail'}

    r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)
