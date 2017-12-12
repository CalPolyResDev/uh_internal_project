from urllib.parse import quote, urlencode
from ...settings.base import get_env_variable
import base64
import json
import uuid
import time
import requests


graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Client ID and secret
client_id = get_env_variable('UH_INTERNAL_MICROSOFT_APPLICATION_ID')
client_secret = get_env_variable('UH_INTERNAL_MICROSOFT_APPLICATION_SECRET')
tenantId = 'cpslo.onmicrosoft.com' #make this a env var

# Constant strings for OAuth2 flow
# The OAuth authority
authority = 'https://login.microsoftonline.com/'

# The authorize URL that initiates the OAuth2 client credential flow for admin consent
authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

# The token issuing endpoint
#token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')
token_url = "https://login.microsoftonline.com/cpslo.onmicrosoft.com/oauth2/token"

# Admin consent endpoint
permisssions_url = '{0}{1}{2}'.format(authority, tenantId, '/adminconsent?')

def get_token():
    # Build the post form for the token request
    post_data = { 'grant_type': 'client_credentials',
                'scope': "https://graph.microsoft.com", #might have to change to resource
                'client_id': client_id,
                'client_secret': client_secret,
                }

    r = requests.post(token_url, data=post_data)

    try:
        return r.json()['access_token']
    except:
        'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

def get_admin_consent():
    get_data = {'client_id': client_id,
                'state': '12345',
                'redirect_uri': 'https://internal.housing.calpoly.edu/'
    }

    r = requests.get(permisssions_url, params=get_data)

    try:
        print('requesting admin consent')
        print(r.url)
        return r.json()
    except:
        'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

#def get_email
