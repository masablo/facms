## setup

### data_allocation

```shell
pipenv --python 3.7.0
pipenv shell
pipenv install requests BeautifulSoup4 lxml pyyaml pandas selenium
pipenv install oauth2client google-api-python-client google-cloud-storage gspread
pipenv install "python-dotenv~=0.13.0"
pipenv install "chromedriver-binary==83.0.4103.39.0"
# pipenv install scrapy
# pipenv install --dev tox flake8 autopep8 pytest coverage black==18.9b0
pip freeze > requirements.txt

cat << EOS >> .env
CMS_ID=xxxxxxxx
CMS_PS=xxxxxxxx
LOGIN=xxxxxxxx
ARTICLE=xxxxxxxx
UA=xxxxxxxx
CLIENT_SECRET_FILE=/path/to/client_secret.json
CREDENTIAL_FILE=/path/to/credentials.json
KEY_FILE_LOCATION=/path/to/project-name-xxxxxxx.json
FOLDER_ID=cms_folder_id
REPORT_ID=report_folder_id
FA_ID=fa_folder_id
APP_ID=app_id
ARTCILE_ID=article_spreadsheet_id
ARTICLE_RANGE=xxxxxxxx
TIMELINE_ID=timeline_spreadsheet_id
TIMELINE_RANGE=xxxxxxxx
ANALYTICS_ID=view_id
PROJECT_ID=project_id
FIREBASE_ID=firebase_id
APPLICATION_NAME=xxxxxxxx
PIN=xxxxxxxx
EMAIL=xxxxxxxx
PASSWORD=xxxxxxxx
EOS

# Once you change the .env, you need to `exit` and then `pipenv shell` again to reflect it

# You need to share the google drive folder with the service accounts to create a spredsheet in it

# Cloud functions use your-project-name@appspot.gserviceaccount.com by default
# the default timeout is 60 sec (you can change it up to 540 sec)
# Cron job send a POST request to the Cloud functions
# curl -X POST "https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/FUNCTION_NAME" \
#      -H "Content-Type:application/json"

gcloud functions deploy main --runtime python37 --trigger-http --timeout=540

brew install oath-toolkit
oathtool --totp --base32 [key (32 characters)]

pip show chromedriver-binary | grep "Version: 83"
```

---

## references

### General

[Google Cloud API](https://cloud.google.com/apis/docs/overview?hl=en)

[Authentication overview](https://cloud.google.com/docs/authentication?hl=en)

[OAuth 2.0](https://cloud.google.com/docs/authentication/end-user?hl=en)

[service accounts](https://cloud.google.com/iam/docs/service-accounts?hl=en)

- client_secret.json (Google APIs OAuth 2.0 client ID - APPLICATION_NAME) -> credentials.json
- project-name-xxxxxxx.json (Google APIs service accounts)
  - xxx@appspot.gserviceaccount.com (App Engine default service account)
  - xxx@project-name.iam.gserviceaccount.com (user-managed service account)

[Pricing](https://cloud.google.com/pricing/list?hl=en)

### Google Analytics

[Account Explorer for checking the view id](https://ga-dev-tools.appspot.com/account-explorer/)

[Dimensions & Metrics Explorer](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/?hl=en)

[Core Reporting API - Common Queries](https://developers.google.com/analytics/devguides/reporting/core/v3/common-queries?hl=en)

### Cloud Functions

[Calling Cloud functions - HTTP Triggers](https://cloud.google.com/functions/docs/calling/http?hl=en)

[Cron Job](https://cron-job.org/)

[Google Apps Script - Time-driven triggers](https://developers.google.com/apps-script/guides/triggers/installable#time-driven_triggers)

[CircleCI - Using Workflows to Schedule Jobs](https://circleci.com/docs/2.0/workflows/)

### Selenium

[ChromeDriver - WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/home)

[Selenium with Python](https://selenium-python.readthedocs.io/)
