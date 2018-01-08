import os
from os.path import join, dirname
from ...settings.base import get_env_variable

# https://github.com/fedorareis/pyexchange This is a combination of a few branches and some custom code
from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection, ExchangeBasicAuthConnection

URL = get_env_variable('RESNET_INTERNAL_OUTLOOK_URL')
USERNAME = get_env_variable('RESNET_INTERNAL_EMAIL_OUT_USERNAME')  # ResNet username
PASSWORD = get_env_variable('RESNET_INTERNAL_EMAIL_OUT_PASSWORD')  # ResNet Password


def setup():
    """ Creates the Exchange Connection """
    # Set up the connection to Exchange
    connection = ExchangeBasicAuthConnection(url=URL,
                                             username=USERNAME,
                                             password=PASSWORD)

    service = Exchange2010Service(connection)

    return service


def get_mail(service):
    
    folder = service.folder()
    folder_id = "inbox"
    email = folder.get_folder(folder_id)

    return email.total_count

def get_voicemail(service):
    
    folder = service.folder()
    voicemail_folder_id = "AAMkADk3MzI3ZmNiLTM5YzMtNGZlOS1hZjVkLTFhN2I5ZTBjNmFmOAAuAAAAAACiNxZPdHhiS6q1zMiCAUIaAQBCzAjvjx3GTKwjaiEZoJadAAADOUuhAAA="
    voicemail = folder.get_folder(voicemail_folder_id)

    return voicemail.total_count
