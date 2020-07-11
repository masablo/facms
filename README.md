## TOC

- [setup](https://github.com/masablo/facms#setup)

  - [data_allocation](https://github.com/masablo/facms#data_allocation)

- [references](https://github.com/masablo/facms#references)
  - [General](https://github.com/masablo/facms#general)
  - [Google (Firebase) Analytics](https://github.com/masablo/facms#google-analytics)
  - [Cloud Functions](https://github.com/masablo/facms#cloud-functions)
  - [Selenium](https://github.com/masablo/facms#selenium)
  - [Scrapy](https://github.com/masablo/facms#scrapy)

---

## setup

### data_allocation

```shell
pipenv --python 3.7.0
pipenv shell
pipenv sync --dev
# pipenv install requests BeautifulSoup4 lxml pyyaml pandas selenium schedule cerberus
# pipenv install oauth2client google-api-python-client google-cloud-storage gspread
# pipenv install "python-dotenv~=0.13.0"
# pipenv install "chromedriver-binary==83.0.4103.39.0"
# pipenv install scrapy ipython
# pipenv install --dev tox flake8 autopep8 pytest coverage black==18.9b0
pipenv run pip freeze > requirements.txt

cat << EOS >> .env
CMS_ID=xxxxxxxx
CMS_PS=xxxxxxxx
LOGIN=xxxxxxxx
ARTICLE=xxxxxxxx
WEB=xxxxxxxx
APP=xxxxxxxx
SLACK_WEBHOOK=https://hooks.slack.com/services/<team_id>/Bxxxxxxxx/xxxxxxxx
SLACK_PINGME=https://hooks.slack.com/services/<team_id>/Bxxxxxxxx/xxxxxxxx
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
# the default memory is 256MB (you can change it up to 2GB)

# Cron job send a POST request to the Cloud functions
# curl -X POST "https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/FUNCTION_NAME" \
#      -H "Content-Type:application/json"

gcloud functions deploy main --runtime python37 --trigger-http --timeout=540 --memory=2048MB

brew install oath-toolkit
oathtool --totp --base32 [key (32 characters)]

brew install telnet

pipenv run pip show chromedriver-binary | grep "Version: 83"
pipenv run pip list | grep -e Scrapy -e Twisted -e lxml -e pyOpenSSL
pipenv run pip show requests-html | grep "Requires"

# scrapy project (Global commands)
scrapy -h
scrapy startproject [project_name]
cd gacms
scrapy genspider -l
scrapy genspider [-t template_name][spider_name] [domain]
scrapy settings --get BOT_NAME
scrapy runspider [spider_module_name.py] [-o output_file_name(.json|.jl)]
scrapy shell '[domain]' [--nolog]
scrapy crawl [spider_name] -a [tag_name1=value1] -a [tag_name2=value2]
scrapy parse [url] --spider [spider_name] -c [spider_method] # call spider_method from the spider to prase a page
>>> shelp()
>>> help(scrapy.http.Reuqest)
>>> response.css('title')
>>> response.css('title::text').getall()
>>> response.css('title::text').re(r'')
>>> response.css('li.next a').attrib['href']
>>> response.css('li.next a::attr(href)').get()
>>> response.xpath('//title').get()

# scrapy project (Project-only commands)
scrapy edit [spider_name]
scrapy list
scrapy check -l
scrapy crawl [spider_name] [-o output_file_name(.json|.jl)]
scrapy crawl facms -o articles.csv

telnet localhost 6023
>>> from scrapy.utils.trackref import get_oldest
>>> from scrapy.utils.trackref import iter_all
>>> from scrapy.spiders import Spider
>>> prefs()
>>> prefs(ignore=Spider)
>>> r = get_oldest('HtmlResponse')
>>> r.url
>>> [r.url for r in iter_all('HtmlResponse')]

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

### Google (Firebase) Analytics

[Account Explorer for checking the view id](https://ga-dev-tools.appspot.com/account-explorer/)

[Dimensions & Metrics Explorer](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/?hl=en)

[Core Reporting API - Common Queries](https://developers.google.com/analytics/devguides/reporting/core/v3/common-queries?hl=en)

### Cloud Functions

[gcloud functions deploy - create or update a Google Cloud Function](https://cloud.google.com/sdk/gcloud/reference/functions/deploy?hl=en)

[set memory and timeout to cloud functions on Console](https://stackoverflow.com/a/61739391)

[Calling Cloud functions - HTTP Triggers](https://cloud.google.com/functions/docs/calling/http?hl=en)

- [Cron Job](https://cron-job.org/)

- [Google Apps Script - Time-driven triggers](https://developers.google.com/apps-script/guides/triggers/installable#time-driven_triggers)

- [CircleCI - Using Workflows to Schedule Jobs](https://circleci.com/docs/2.0/workflows/)

### Selenium

[ChromeDriver - WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/home)

[Selenium with Python](https://selenium-python.readthedocs.io/)

### Scrapy

[Architecture overview](https://doc.scrapy.org/en/latest/intro/overview.html)

- [Configuration settings](https://doc.scrapy.org/en/latest/topics/commands.html#configuration-settings)
- [Populating the settings](https://doc.scrapy.org/en/latest/topics/settings.html#populating-the-settings)
- [scrapy.http.Request.meta](https://doc.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request.meta)
- [Request.meta special keys](https://doc.scrapy.org/en/latest/topics/request-response.html#request-meta-special-keys)
- [Using FormRequest.from_response() to simulate a user login](https://doc.scrapy.org/en/latest/topics/request-response.html#using-formrequest-from-response-to-simulate-a-user-login)
- [scrapy/itemadapter](https://github.com/scrapy/itemadapter/)
- [Item Pipeline](https://doc.scrapy.org/en/latest/topics/item-pipeline.html)
- [Item Exporters](https://doc.scrapy.org/en/latest/topics/exporters.html)
- [Feed exports](https://doc.scrapy.org/en/latest/topics/feed-exports.html)
- [Telnet Console](https://doc.scrapy.org/en/latest/topics/telnetconsole.html)
- [Core API](https://doc.scrapy.org/en/latest/topics/api.html)
- [Custom Contracts](https://doc.scrapy.org/en/latest/topics/contracts.html#custom-contracts)
- [Run Scrapy from a script](https://doc.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script)
- [Avoiding getting banned](https://doc.scrapy.org/en/latest/topics/practices.html#avoiding-getting-banned)
- [Selecting dynamically-loaded content](https://doc.scrapy.org/en/latest/topics/dynamic-content.html)
- [Debugging memory leaks](https://doc.scrapy.org/en/latest/topics/leaks.html)
- [Downloader Middleware](https://doc.scrapy.org/en/latest/topics/downloader-middleware.html)
- [Spider Middleware](https://doc.scrapy.org/en/latest/topics/spider-middleware.html)

[Splash - A javascript rendering service](https://splash.readthedocs.io/en/stable/)

[Scrapyd](https://scrapyd.readthedocs.io/en/latest/)

[QuotesBot](https://github.com/scrapy/quotesbot)

[The ScrapingHub BLOG](https://blog.scrapinghub.com/)
