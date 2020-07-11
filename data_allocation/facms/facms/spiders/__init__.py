import os
from dotenv import load_dotenv
load_dotenv()

from apiclient.discovery import build
import oauth2client
from oauth2client import file as oauthFile
from oauth2client import tools as oauthTool
from oauth2client.service_account import ServiceAccountCredentials

CMS_ID=os.getenv('CMS_ID')
CMS_PS=os.getenv('CMS_PS')
LOGIN=os.getenv('LOGIN')
ARTICLE=os.getenv('ARTICLE')
# CREDENTIAL_FILE=os.getenv('CREDENTIAL_FILE')
CREDENTIAL_FILE='credentials.json'
GKEY=os.getenv('KEY_FILE_LOCATION')
FOLDER_ID=os.getenv('FOLDER_ID')
REPORT_ID=os.getenv('REPORT_ID')
FA_ID=os.getenv('FA_ID')
APP_ID=os.getenv('APP_ID')
ANALYTICS_ID=os.getenv('ANALYTICS_ID')
PROJECT_ID=os.getenv('PROJECT_ID')
FIREBASE_ID=os.getenv('FIREBASE_ID')
DASHBOARD_NAME=os.getenv('DASHBOARD_NAME')
APPLICATION_NAME=os.getenv('APPLICATION_NAME')


class GoogleApi:

    DIRNAME = os.path.dirname(__file__)

    @classmethod
    def get_service(self, api_name, api_version, scopes):
        key_file_location = os.path.join(self.DIRNAME, GKEY.replace('./data/', ''))
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes=scopes)
        service = build(api_name, api_version, credentials=credentials, cache_discovery=False)
        return service

    @classmethod
    def get_credentials(self):
        store = oauthFile.Storage(os.path.join(self.DIRNAME, CREDENTIAL_FILE))
        credentials = store.get()
        return credentials
