import os
from dotenv import load_dotenv
load_dotenv()
# load_dotenv(verbose=True)

# from pathlib import Path  # python3 only
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

ID=os.getenv('ID')
PS=os.getenv('PS')
LOGIN=os.getenv('LOGIN')
ARTICLE=os.getenv('ARTICLE')
TIMELINE=os.getenv('TIMELINE')
UA=os.getenv('UA')
GKEY=os.getenv('KEY_FILE_LOCATION')
FOLDER_ID=os.getenv('FOLDER_ID')
SPREADSHEET_ID=os.getenv('SPREADSHEET_ID')
ANALYTICS_ID=os.getenv('ANALYTICS_ID')
APPLICATION_NAME=os.getenv('APPLICATION_NAME')

HEADER={'User-Agent': UA}
CLIENT_SECRET_FILE='client_secret.json'
CREDENTIAL_FILE='./credential.json'
RANGE_NAME='A1'
MAJOR_DIMENSION='ROWS'
