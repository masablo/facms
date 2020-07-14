import os
from dotenv import load_dotenv
load_dotenv()
# load_dotenv(verbose=True)

# from pathlib import Path  # python3 only
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

CMS_ID=os.getenv('CMS_ID')
CMS_PS=os.getenv('CMS_PS')
LOGIN=os.getenv('LOGIN')
ARTICLE=os.getenv('ARTICLE')
TIMELINE=os.getenv('TIMELINE')
WEB=os.getenv('WEB')
WEBAPI=os.getenv('WEBAPI')
APP=os.getenv('APP')
SLACK_WEBHOOK=os.getenv('SLACK_WEBHOOK')
SLACK_PINGME=os.getenv('SLACK_PINGME')
UA=os.getenv('UA')
CLIENT_SECRET_FILE=os.getenv('CLIENT_SECRET_FILE')
CREDENTIAL_FILE=os.getenv('CREDENTIAL_FILE')
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
PIN=os.getenv('PIN')
EMAIL=os.getenv('EMAIL')
PASSWORD=os.getenv('PASSWORD')

HEADER={'User-Agent': UA}
RANGE_NAME='A1'
MAJOR_DIMENSION='ROWS'
ARTICLE_ID_LENGTH=5
ARTICLE_PATH='/Timeline/ArticleView/'
