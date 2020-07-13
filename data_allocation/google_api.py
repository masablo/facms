import config
import argparse

from apiclient.discovery import build
import oauth2client
from oauth2client import file as oauthFile
from oauth2client import tools as oauthTool
from oauth2client.service_account import ServiceAccountCredentials


def get_service(api_name, api_version, scopes):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """
    key_file_location = config.GKEY
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes=scopes)
    service = build(api_name, api_version, credentials=credentials, cache_discovery=False)
    return service


def get_credentials():
    store = oauthFile.Storage(config.CREDENTIAL_FILE)
    credentials = store.get()
    # make a credentials.json (token.pickle) if it is not in the current directory
    if not credentials or credentials.invalid:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
                  'https://www.googleapis.com/auth/analytics.readonly',
                  'https://www.googleapis.com/auth/drive',
                  'https://www.googleapis.com/auth/drive.file',
                  'https://www.googleapis.com/auth/drive.metadata',
                  'https://www.googleapis.com/auth/drive.appdata']
        flow = oauth2client.client.flow_from_clientsecrets(config.CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = config.APPLICATION_NAME
        args = '--auth_host_name localhost --logging_level INFO --noauth_local_webserver'
        flags = argparse.ArgumentParser(parents=[oauthTool.argparser]).parse_args(args.split())
        return oauthTool.run_flow(flow, store, flags)
    return credentials
