from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests
import logging
import logging.config
# import pickle
import csv
import sys
import yaml
import config
import time
import re

from google_api import get_service


logging.config.dictConfig(yaml.load(open("log_conf.yaml").read(), Loader=yaml.SafeLoader))
logger = logging.getLogger(__name__)


def export_csv(name, head, articles):
    with open('./data/{}'.format(name), 'w') as csv_file:
        header = head
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        for row in articles:
            writer.writerow(row)


def make_sheet_in_drive():
    file_metadata = {
        'name': name,
        'parents': [config.FOLDER_ID],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    serviceDrive = get_service(api_name='drive',
                               api_version='v3',
                               scopes=['https://www.googleapis.com/auth/drive',
                                       'https://www.googleapis.com/auth/drive.file',
                                       'https://www.googleapis.com/auth/drive.appdata'])
    return serviceDrive.files().create(body=file_metadata, fields='id').execute()


def add_data_to_sheet(sheet, data):
    body = {
        "range": config.RANGE_NAME,
        "majorDimension": config.MAJOR_DIMENSION,
        "values": data
    }
    serviceSheet = get_service(api_name='sheets',
                               api_version='v4',
                               scopes=['https://www.googleapis.com/auth/spreadsheets'])
    resource = serviceSheet.spreadsheets().values()
    resource.append(spreadsheetId=sheet.get('id'),
        range=config.RANGE_NAME, valueInputOption='USER_ENTERED', body=body).execute()


def upload_todays_csv(name, data):
    sheet = make_sheet_in_drive()
    logging.info(sheet.get('id'))
    add_data_to_sheet(sheet, data)


def get_payload(s):
    res = s.get(config.LOGIN, headers=config.HEADER)
    soup = bs(res.text, features='lxml')
    token = soup.find(attrs={'name': 'testcookie'}).get('value')
    payload = {
        'log': config.ID,
        'pwd': config.PS,
        'wp-submit': 'Log In',
        'redirect_to': 'https://nikkei-asianreview.express.pugpig.com/wp-admin/',
        'testcookie': token
    }
    return payload


def login(s):
    payload = get_payload(s)
    res = s.post(config.WPLOGIN, data=payload, headers=config.HEADER)
    soup = bs(res.text, features='lxml')
    logger.info('Login Success!: {}'.format(soup.title.text))


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


def extract_timeline(p):
    keys = [key.find('strong').text for key in p.find_all('td', attrs={'data-colname': 'Description'})]
    names = [name.find('strong').text for name in p.find_all('td', attrs={'data-colname': 'Timeline Title'})]
    return (keys, names)

def export_todays_articles(s):
    logger.info('export_todays_articles')
    res = s.get(config.ARTICLE, headers=config.HEADER)
    parse = bs(res.text, features='lxml')
    articles = []
    today = True
    page_index = 1

    while today:
        r = s.get(config.ARTICLE + '?paged={}'.format(page_index), headers=config.HEADER)
        p = bs(r.text, features='lxml')
        (keys, titles, authors, kinds, tags, sections, dates) = extract_article(p)
        today = check_today(dates)
        index = get_index(dates)
        for i in range(index):
            articles.append([keys[i], titles[i], authors[i], kinds[i], tags[i], sections[i], dates[i]])
        logger.info('page {} is finished'.format(page_index))
        page_index += 1
        time.sleep(1.5)

    articles.insert(0, ['key', 'title', 'author', 'type', 'tag', 'section', 'date'])
    upload_todays_csv('{}'.format(datetime.today().strftime('%Y-%m-%d')), articles)


def export_all_articles(s):
    logger.info('export_all_articles')
    res = s.get(config.ARTICLE, headers=config.HEADER)
    parse = bs(res.text, features='lxml')
    total = int(parse.find('span', attrs={'class': 'total-pages'}).text)
    articles = []
    for i in range(1, total):
        logger.info('page {} is finished'.format(i))
        r = s.get(config.ARTICLE + '?paged={}'.format(i), headers=config.HEADER)
        p = bs(r.text, features='lxml')
        (keys, titles, authors, kinds, tags, sections, dates) = extract_article(p)
        for key, title, author, kind, tag, section, date in zip(keys, titles, authors, kinds, tags, sections, dates):
            articles.append({'key': key,
                             'title': title,
                             'author': author,
                             'type': kind,
                             'tag': tag,
                             'section': section,
                             'date': date})
    export_csv('articles.csv', ['key', 'title', 'author', 'type', 'tag', 'section', 'date'], articles)


def export_all_timelines(s):
    logger.info('export_all_timelines')
    res = s.get(config.TIMELINE, headers=config.HEADER)
    parse = bs(res.text, features='lxml')
    total = int(parse.find('span', attrs={'class': 'total-pages'}).text)
    timelines = []
    for i in range(1, total + 1):
        logger.info('page {} is finished'.format(i))
        r = s.get(config.TIMELINE+ '&paged={}'.format(i), headers=config.HEADER)
        p = bs(r.text, features='lxml')
        (keys, names) = extract_timeline(p)
        for key, name in zip(keys, names):
            timelines.append({'key': key, 'name': name})
    export_csv('timelines.csv', ['key', 'name'], timelines)


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) == 2 else None
    if arg in ['all', 'timeline', 'today']:
        s = requests.session()
        login(s)
        if arg == 'all':
            export_all_articles(s)
        elif arg == 'timeline':
            export_all_timelines(s)
        elif arg == 'today':
            export_todays_articles(s)
    logger.error('please give one argument out of three (all, timeline, today)')
