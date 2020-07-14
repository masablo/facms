from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests
import time
import re
import os
import httplib2
import logging

from apiclient.discovery import build
from oauth2client.client import GoogleCredentials


HEADER = {'User-Agent': os.getenv('UA')}


def get_credentials():
    return GoogleCredentials.get_application_default()


def make_sheet_in_dirve(credentials, name):
    file_metadata = {
        'name': name,
        'parents': [os.getenv('FOLDER_ID')],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    serviceDrive = build('drive', 'v3', credentials=credentials, cache_discovery=False)
    return serviceDrive.files().create(body=file_metadata, fields='id').execute()


def add_data_to_sheet(sheet, data, credentials):
    body = {
        "range": os.getenv('RANGE_NAME'),
        "majorDimension": os.getenv('MAJOR_DIMENSION'),
        "values": data
    }
    serviceSheet = build('sheets', 'v4', credentials=credentials)
    resource = serviceSheet.spreadsheets().values()
    resource.append(spreadsheetId=sheet.get('id'),
        range=os.getenv('RANGE_NAME'), valueInputOption='USER_ENTERED', body=body).execute()


def upload_todays_sheet(name, data):
    credentials = get_credentials()
    sheet = make_sheet_in_dirve(credentials, name)
    logging.info(sheet.get('id'))
    add_data_to_sheet(sheet, data, credentials)


def get_payload(s):
    res = s.get(os.getenv('LOGIN'), headers=HEADER)
    soup = bs(res.text, features='lxml')
    token = soup.find(attrs={'name': 'testcookie'}).get('value')
    payload = {
        'log': os.getenv('ID'),
        'pwd': os.getenv('PS'),
        'wp-submit': 'Log In',
        'redirect_to': 'https://nikkei-asianreview.express.pugpig.com/wp-admin/',
        'testcookie': token
    }
    return payload


def login(s):
    payload = get_payload(s)
    res = s.post(os.getenv('WPLOGIN'), data=payload, headers=HEADER)
    soup = bs(res.text, features='lxml')
    logging.info('Login Success!: {}'.format(soup.title.text))


def check_today(dates):
    return len([date for date in dates if 'ago' in date]) is len(dates)


def get_index(dates):
    d = [index for index, date in enumerate(dates) if 'ago' in date]
    return len(dates) if len(d) is len(dates) else len(d)


def extract_article(p):
    keys = [re.search('post=([0-9]*)', key.find('a').get('href'))[1]
        for key in p.find_all('td', attrs={'data-colname': 'Title'})]
    titles = [title.find('a').text for title in p.find_all('td', attrs={'data-colname': 'Title'})]
    authors = [author.text for author in p.find_all('td', attrs={'data-colname': 'Author'})]
    kinds = [kind.text for kind in p.find_all('td', attrs={'data-colname': 'Article Types'})]
    tags = ['+'.join([tag.text for tag in taglist.find_all('a')])
            for taglist in p.find_all('td', attrs={'data-colname': 'Timeline Tags'})]
    sections = [section.text for section in p.find_all('td', attrs={'data-colname': 'Sections'})]
    dates = [date.find('span').text for date in p.find_all('td', attrs={'data-colname': 'Date'})]
    return (keys, titles, authors, kinds, tags, sections, dates)


def export_todays_articles(s):
    res = s.get(os.getenv('ARTICLE'), headers=HEADER)
    parse = bs(res.text, features='lxml')
    articles = []
    today = True
    page_index = 1

    while today:
        r = s.get('{}?paged={}'.format(os.getenv('ARTICLE'), page_index), headers=HEADER)
        p = bs(r.text, features='lxml')
        (keys, titles, authors, kinds, tags, sections, dates) = extract_article(p)
        today = check_today(dates)
        index = get_index(dates)
        for i in range(index):
            articles.append([keys[i], titles[i], authors[i], kinds[i], tags[i], sections[i], dates[i]])
        page_index += 1
        logging.info(page_index)
        time.sleep(1.5)

    articles.insert(0, ['key', 'title', 'author', 'type', 'tag', 'section', 'date'])
    name = datetime.now()
    upload_todays_sheet('{}'.format(name.strftime('%Y-%m-%d')), articles)


def main(request):
    s = requests.session()
    login(s)
    export_todays_articles(s)