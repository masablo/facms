## setup

```shell
pipenv --python 3.7.0
pipenv shell
pipenv install requests BeautifulSoup4 lxml
pipenv install oauth2client google-api-python-client google-cloud-storage
pipenv install "python-dotenv~=0.13.0"
# pipenv install scrapy
# pipenv install --dev tox flake8 autopep8 pytest coverage black==18.9b0
pip freeze > requirements.txt

cat << EOS >> .env
ID=xxxxxxxx
PS=xxxxxxxx
LOGIN=xxxxxxxx
ARTICLE=xxxxxxxx
UA=xxxxxxxx
KEY_FILE_LOCATION=/path/to/project-name-xxxxxxx.json
FOLDER_ID=google_drive_folder_id
SPREADSHEET_ID=spred_sheet_id
ANALYTICS_ID=view_id
APPLICATION_NAME=xxxxxxxx
EOS

# Once you change the .env, you need to `exit` and then `pipenv shell` again to reflect it

# You need to share the google drive folder with the service accounts to create a spredsheet in it

# Cloud functions use your-project-name@appspot.gserviceaccount.com by default
# Cron job send a POST request to the Cloud functions
# curl -X POST "https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/FUNCTION_NAME" \
#      -H "Content-Type:application/json"
```

---

## documents

### General

[Google Cloud API](https://cloud.google.com/apis/docs/overview?hl=en)

[Authentication overview](https://cloud.google.com/docs/authentication?hl=en)

[OAuth 2.0](https://cloud.google.com/docs/authentication/end-user?hl=en)

[service accounts](https://cloud.google.com/iam/docs/service-accounts?hl=en)

- client_secret.json (Google APIs OAuth 2.0 client ID - APPLICATION_NAME) -> credentials.json
- project-name-xxxxxxx.json (Google APIs service accounts)
  - xxx@appspot.gserviceaccount.com (App Engine default service account)
  - xxx@project-name.iam.gserviceaccount.com (a user-managed service account)

### Google Analytics

[Account Explorer for checking the view id](https://ga-dev-tools.appspot.com/account-explorer/)

[Dimensions & Metrics Explorer](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/?hl=en)

[Core Reporting API - Common Queries](https://developers.google.com/analytics/devguides/reporting/core/v3/common-queries?hl=en)

### Cloud Functions

[Calling Cloud functions - HTTP Triggers](https://cloud.google.com/functions/docs/calling/http?hl=en)

[Cron Job](https://cron-job.org/)
