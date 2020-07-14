from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import requests
import asyncio
import logging
import logging.config
import csv
import sys
import yaml
import config
import time
import re

from google_api import get_service


logging.config.dictConfig(yaml.load(open("../log_conf.yaml").read(), Loader=yaml.SafeLoader))
logger = logging.getLogger(__name__)


def get_article_id(article_id):
    pattern = re.compile('page-([0-9]{{{}}})'.format(config.ARTICLE_ID_LENGTH))
    return int(re.search(pattern, article_id)[1]) if re.search(pattern, article_id) else None
    # return int(article_id.replace('page-', '')) if len(article_id.replace('page-', '')) == config.ARTICLE_ID_LENGTH else None


def make_report(report_id):
    timelines = pd.read_csv('./data/timelines.csv')
    logging.info('timelines is loaded')
    articles = pd.read_csv('./data/articles.csv')
    logging.info('articles is loaded')
    pv = pd.read_csv('./data/analytics/{}.csv'.format(report_id), names=('url', 'pv'))
    logging.info('{}.csv is loaded'.format(report_id))

    key_name = dict(zip(timelines.key.to_list(), timelines.name.to_list()))
    key_title = dict(zip(articles.key.to_list(), articles.title.to_list()))
    article_pv = dict(zip(pv.url[pv.url.str.startswith(config.ARTICLE_PATH)].to_list(), pv.pv[pv.url.str.startswith(config.PATH)].to_list()))
    data = []
    head = ['TimelineID', 'TimelineName', 'ArticleID', 'Headline', 'PV']
    for url in article_pv:
        path, timeline_id, article_id = url.rsplit('/', 2)
        data.append({'TimelineID': url,
                     'TimelineName': key_name.get(timeline_id, 'unknown'),
                     'ArticleID': get_article_id(article_id) if get_article_id(article_id) else 'unknown',
                     'Headline': key_title.get(get_article_id(article_id), 'unknown') if get_article_id(article_id) else 'unknown',
                     'PV': article_pv.get(url)})
    pv_data = [row for row in data if row['TimelineName'] != 'unknown' and row['Headline'] != 'unknown']
    export_csv('reports/{}.csv'.format(report_id), head, pv_data)


def export_csv(name, head, articles):
    with open('./data/{}'.format(name), 'w') as csv_file:
        header = head
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        for row in articles:
            writer.writerow(row)
    sys.exit()


def make_sheet_in_drive(name):
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
    sheet = make_sheet_in_drive(name)
    logging.info(sheet.get('id'))
    add_data_to_sheet(sheet, data)
    sys.exit()


def get_payload(s):
    res = s.get(config.LOGIN, headers=config.HEADER)
    soup = bs(res.text, features='lxml')
    token = soup.find(attrs={'name': 'testcookie'}).get('value')
    payload = {
        'log': config.CMS_ID,
        'pwd': config.CMS_PS,
        'wp-submit': 'Log In',
        'redirect_to': 'https://nikkei-asianreview.express.pugpig.com/wp-admin/',
        'testcookie': token
    }
    return payload


def login(s):
    payload = get_payload(s)
    res = s.post(config.LOGIN, data=payload, headers=config.HEADER)
    soup = bs(res.text, features='lxml')
    logger.info('Login Success!: {}'.format(soup.title.text))


def is_today(dates):
    return len([date for date in dates if 'ago' in date]) is len(dates)


def get_index(dates):
    d = [index for index, date in enumerate(dates) if 'ago' in date]
    return len(dates) if len(d) is len(dates) else len(d)


def extract_article_meta(p):
    keys = [re.search('post=([0-9]*)', key.find('a').get('href'))[1]
        for key in p.find_all('td', attrs={'data-colname': 'Title'})]
    titles = [title.find('a').text for title in p.find_all('td', attrs={'data-colname': 'Title'})]
    authors = [author.text for author in p.find_all('td', attrs={'data-colname': 'Author'})]
    kinds = [kind.text for kind in p.find_all('td', attrs={'data-colname': 'Article Types'})]
    tags = ['+'.join([tag.text for tag in taglist.find_all('a')])
            for taglist in p.find_all('td', attrs={'data-colname': 'Timeline Tags'})]
    sections = [section.text for section in p.find_all('td', attrs={'data-colname': 'Sections'})]
    dates = [date.find('span').text for date in p.find_all('td', attrs={'data-colname':'Date'})]
    return keys, titles, authors, kinds, tags, sections, dates


def extract_article(page_index, s):
    r = s.get(config.ARTICLE + '?paged={}'.format(page_index), headers=config.HEADER)
    p = bs(r.text, features='lxml')
    articles = []
    (keys, titles, authors, kinds, tags, sections, dates) = extract_article_meta(p)
    for key, title, author, kind, tag, section, date in zip(keys, titles, authors, kinds, tags, sections, dates):
        articles.append({'key': key, 'title': title, 'author': author, 'type': kind, 'tag': tag, 'section': section, 'date': date})
    logger.info('page {} is finished'.format(page_index))
    return articles


def extract_timeline(page_index):
    r = s.get(config.TIMELINE + '&paged={}'.format(page_index), headers=config.HEADER)
    p = bs(r.text, features='lxml')
    timelines = []
    keys = [key.find('strong').text for key in p.find_all('td', attrs={'data-colname': 'Description'})]
    names = [name.find('strong').text for name in p.find_all('td', attrs={'data-colname': 'Timeline Title'})]
    for key, name in zip(keys, names):
        timelines.append({'key': key, 'name': name})
    logger.info('page {} is finished'.format(page_index))
    return timelines


def export_todays_articles(s):
    logger.info('export_todays_articles')
    res = s.get(config.ARTICLE, headers=config.HEADER)
    parse = bs(res.text, features='lxml')
    logger.info(parse.title.text)
    articles = []
    today = True
    page_index = 1

    while today:
        r = s.get(config.ARTICLE + '?paged={}'.format(page_index), headers=config.HEADER)
        p = bs(r.text, features='lxml')
        (keys, titles, authors, kinds, tags, sections, dates) = extract_article_meta(p)
        today = is_today(dates)
        index = get_index(dates)
        for i in range(index):
            articles.append([keys[i], titles[i], authors[i], kinds[i], tags[i], sections[i], dates[i]])
        logger.info('page {} is finished'.format(page_index))
        page_index += 1
        time.sleep(1.5)

    articles.insert(0, ['key', 'title', 'author', 'type', 'tag', 'section', 'date'])
    upload_todays_csv('{}'.format(datetime.today().strftime('%Y-%m-%d')), articles)


async def export_all_articles(loop, s):
    logger.info('export_all_articles')
    res = s.get(config.ARTICLE, headers=config.HEADER)
    parse = bs(res.text, features='lxml')
    logger.info(parse.title.text)
    total = int(parse.find('span', attrs={'class': 'total-pages'}).text) + 1
    async def scraping(page_index):
        async with asyncio.Semaphore(10):
            return await loop.run_in_executor(None, extract_article, page_index, s)
    articles = [scraping(page_index) for page_index in range(1, total)]
    return await asyncio.gather(*articles)


async def export_all_timelines(loop, s):
    logger.info('export_all_timelines')
    res = s.get(config.TIMELINE, headers=config.HEADER)
    parse = bs(res.text, features='lxml')
    logger.info(parse.title.text)
    total = int(parse.find('span', attrs={'class': 'total-pages'}).text) + 1
    async def scraping(page_index):
        async with asyncio.Semaphore(10):
            return await loop.run_in_executor(None, extract_timeline, page_index)
    timelines = [scraping(page_index) for page_index in range(1, total)]
    return await asyncio.gather(*timelines)


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) == 2 else None
    if arg and re.match(r'[0-9]{4}', arg):
        make_report(arg)
    elif arg == 'all':
        s = requests.session()
        login(s)
        loop = asyncio.get_event_loop()
        articles = loop.run_until_complete(export_all_articles(loop, s))
        export_csv('articles.csv', ['key', 'title', 'author', 'type', 'tag', 'section', 'date'], sum(articles, []))
    elif arg == 'timeline':
        s = requests.session()
        login(s)
        loop = asyncio.get_event_loop()
        timelines = loop.run_until_complete(export_all_timelines(loop, s))
        export_csv('timelines.csv', ['key', 'name'], sum(timelines, []))
    elif arg == 'today':
        s = requests.session()
        login(s)
        export_todays_articles(s)
    logger.error('please give one argument out of "all", "timeline", "today", "report_id"')
