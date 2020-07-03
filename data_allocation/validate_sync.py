from bs4 import BeautifulSoup as bs
from datetime import datetime
from cerberus import Validator
# from requests_html import AsyncHTMLSession
import logging
import logging.config
import yaml
import requests, json
import config
import re
import schedule, time


logging.config.dictConfig(yaml.load(open("log_conf.yaml").read(), Loader=yaml.SafeLoader))
logger = logging.getLogger(__name__)


ARTICLE_SCHEMA = {
    'headline': {
        'type': 'string',
        'required': True
    },
    'href': {
        'type': 'string',
        'required': True
    },
    'tag': {
        'type': 'string',
        'required': True
    }
}


WEB_ARTICLE_SCHEMA = {
    'id': {
        'type': 'string',
        'empty': False
    },
    'headline': {
        'type': 'string',
        'empty': False
    },
    'url': {
        'type': 'string',
        'empty': False
    },
    'image': {
        'type': 'dict',
        'schema': {
            'name': {'type': 'string'},
            'caption': {'type': 'string'},
            'credit': {'type': 'string'},
            'fullCaption': {'type': 'string'},
            'imageUrl': {'type': 'string'},
            'variation': {'type': 'string'},
            'expiresAt': {'type': 'datetime',
                          'coerce': lambda d: datetime.fromtimestamp(d),
                          'nullable': True}
        },
        'nullable': True
    },
    'thumbnailImage': {
        'type': 'dict',
        'schema': {
            'name': {'type': 'string'},
            'caption': {'type': 'string'},
            'credit': {'type': 'string'},
            'fullCaption': {'type': 'string'},
            'imageUrl': {'type': 'string'},
            'variation': {'type': 'string'},
            'expiresAt': {'type': 'datetime',
                          'coerce': lambda d: datetime.fromtimestamp(d),
                          'nullable': True}
        },
        'nullable': True
    },
    'primaryTag': {
        'type': 'dict',
        'schema': {
            'remoteId': {'type': 'string', 'empty': False},
            'name': {'type': 'string', 'empty': False}
        },
        'empty': False
    },
    'subhead': {
        'type': 'string',
        'empty': False
    },
    'expiresAt': {
        'type': 'datetime',
        'coerce': lambda d: datetime.fromtimestamp(d)
    }
}

WEB_BLOCKS_SCHEMA = {
    'id': {
        'type': 'string',
        'nullable': True
    },
    'name': {
        'type': 'string',
        'nullable': True
    },
    'neoGenre': {
        'type': 'string',
        'nullable': True
    },
    'headerImage': {
        'type': 'string',
        'nullable': True
    },
    'collectionBlocks': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'view': {'type': 'string', 'empty': False},
                'items': {'type': 'list', 'empty': False}
            }
        }
    },
    'page': {
        'type': 'dict',
        'nullable': True
    },
    'description': {
        'type': 'string',
        'nullable': True
    },
    'isTopic': {
        'type': 'boolean'
    },
    'url': {
        'type': 'string'
    },
    'lastModifiedDate': {
       'type': 'datetime',
       'coerce': lambda d: datetime.fromtimestamp(d)
    }
}

APP_STORY_SCHEMA = {
    'id': {'type': 'string'},
    'type': {'type': 'string'},
    'title': {'type': 'string'},
    'draft': {'type': 'boolean'},
    'section': {'type': 'string'},
    'classes': {'type': 'list', 'schema': {'type': 'string'}},
    'updated': {'type': 'datetime', 'coerce': lambda d: datetime.fromisoformat(d)},
    'published': {'type': 'datetime', 'coerce': lambda d: datetime.fromisoformat(d)},
    'summary': {'type': 'string'},
    'prefetch': {'type': 'list', 'schema': {'type': 'string'}},
    'images': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'ratio': {'type': 'float'},
                'srcset': {'type': 'string'}
            }
        }
    },
    'shareurl': {'type': 'string'},
    'paywall_locked': {'type': 'boolean'},
    'author': {'type': 'string', 'nullable': True},
    'categories': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'scheme': {'type': 'string'},
                'term': {'type': 'string'},
                'label': {'type': 'string'}
            }
        }
    },
    'url': {'type': 'string'}
}

APP_BLOCKS_SCHEMA = {
    'stories': {'type': 'list', 'empty': False},
    'metadata': {
        'type': 'dict',
        'schema': {
            'generated': {
                'type': 'datetime',
                'coerce': lambda d: datetime.fromisoformat(d)
            },
            'atom': {
                'type': 'dict',
                'schema': {
                    'updated': {'type': 'datetime', 'coerce': lambda d: datetime.fromisoformat(d)},
                    'origin_version': {'type': 'string', 'nullable': True},
                    'generator_description': {'type': 'string'}
                }
            }
        }
    },
    'timeline': {
        'type': 'dict',
        'schema': {
            'id': {'type': 'string'},
            'title': {'type': 'string'},
            'classes': {'type': 'list', 'schema': {'type': 'string'}}
        }
    }
}


def _normalize(headline):
    return '{}...'.format(' '.join(re.search(r'//.+/(.+)$', headline)[1].replace('-', ' ').split()[:5]))


def _make_error_message(web, app, not_found_in_web, not_found_in_app, MESSAGE):
    web_message = '*Web articles* \n{}'.format('\n'.join(['{}: <{}|{}>'.format(i+1, w['href'], _normalize(w['href'])) for i,w in enumerate(web)]))
    app_message = '*App articles* \n{}'.format('\n'.join(['{}: <{}|{}>'.format(i+1, a['href'], _normalize(a['href'])) for i,a in enumerate(app)]))
    not_web_message = '*Not Found in Web* \n{}'.format('\n'.join(['{}: <{}|{}>'.format(nw['index'],
                                                                                       nw['href'],
                                                                                       _normalize(nw['href'])) for nw in not_found_in_web]))
    not_app_message = '*Not Found in App* \n{}'.format('\n'.join(['{}: <{}|{}>'.format(na['index'],
                                                                                       na['href'],
                                                                                       _normalize(na['href'])) for na in not_found_in_app]))
    for message in [web_message, app_message, not_web_message, not_app_message]:
        MESSAGE['error']['attachments'][0]['blocks'].append({'type': 'section',
                                                             'text': {'type': 'mrkdwn', 'text': '{}'.format(message)}})
        MESSAGE['error']['attachments'][0]['blocks'].append({'type': 'divider'})
    return MESSAGE['error']


def _notify_to_slack(web, app, not_found_in_web, not_found_in_app):
    MESSAGE = {
        'success': {'attachments': [{'blocks': [{'type':'section',
                                                 'text': {'type': 'mrkdwn', 'text': '*エラーなし*'}}],
                                     'color': '#2eb886'}]},
        'error': {'attachments': [{'blocks': [{'type':'section',
                                               'text': {'type': 'mrkdwn', 'text': '@here \n*エラーが見つかりました*'}},
                                              {'type': 'section',
                                               'text': {'type': 'mrkdwn', 'text': '`{}`'.format(datetime.today().strftime('%Y/%m/%d %H:%M'))}}],
                                   'color': '#D40E0D'}],
    }}
    if len(not_found_in_web) == 0 and len(not_found_in_app) == 0:
        # MESSAGE['success']['attachments'][0]['blocks'].insert(0, {'type': 'section',
        #                                                           'text': {'type': 'mrkdwn',
        #                                                                    'text': '`{}`'.format(datetime.today().strftime('%Y/%m/%d %H:%M'))}})
        # requests.post(config.SLACK_WEBHOOK,
        #               data=json.dumps(MESSAGE['success']))
        return
    requests.post(config.SLACK_PINGME,
                  data=json.dumps(_make_error_message(web, app, not_found_in_web, not_found_in_app, MESSAGE)))


def _log_validation_error_message(err):
    if len(err.keys()) > 0:
        for k, v in err.items():
            for m in v:
                logger.error('{}: {}'.format(k, m))


def validate(web_articles, app_articles):
    not_found_in_web = []
    not_found_in_app = []
    web = [web['href'] for web in web_articles]
    app = [app['href'] for app in app_articles]
    for i,w in enumerate(web_articles):
        if w['href'] not in app:
            w['index'] = i+1
            not_found_in_app.append(w)
    for i,a in enumerate(app_articles):
        if a['href'] not in web:
            a['index'] = i+1
            not_found_in_web.append(a)
    _notify_to_slack(web_articles, app_articles, not_found_in_web, not_found_in_app)


# def wait_render(URL):
#     assesion = AsyncHTMLSession()
#     async def process():
#         res = await assesion.get(URL)
#         await res.html.arender(wait=15, sleep=15)
#         return res
#     res = assesion.run(process)[0]
#     return res.html


def _scraping_web_articles(soup, name):
    targets = soup.find(id=name).select('h2,h4')
    # createdDate, displayDate, lastModifiedDate
    if name == 'opinions':
        return [{'headline': targets[i].find('a').text.strip(),
                 'href': '{}{}'.format(config.WEB, targets[i].find('a').get('href')),
                 'tag': 'Opinion'} for i in range(0, 4)]
    return [{'headline': targets[i+1].find('a').text.strip(),
             'href': '{}{}'.format(config.WEB, targets[i+1].find('a').get('href')),
             'tag': targets[i].text.strip()} for i in range(0, len(targets) - 1, 2)]


def _scraping_app_articles(articles):
    # ids = {'sections-features': 'page-350', 'sections-opinion': 'page-351'}
    # targets = soup.find(id=ids[name])
    return [{'headline': article['title'],
             'href': article['shareurl'],
             'tag': article['section']} for article in articles]


def _extract_web_articles(articles):
    return [{'headline':article['headline'],
             'href': article['url'],
             'tag': article['primaryTag']['name']} for article in articles]


def fetch_web_articles():
    res = requests.get(config.WEB, headers={'User-Agent': config.UA,
                                            'Cache-Control': 'no-store',
                                            'Pragma': 'no-cache'})
    logger.info('web fetched: {}'.format(datetime.today().strftime('%Y/%m/%d %H:%M')))
    soup = bs(res.text, features='lxml')
    topstories = _scraping_web_articles(soup, 'topstories')
    features = _scraping_web_articles(soup, 'features')
    opinions = _scraping_web_articles(soup, 'opinions')
    articles = topstories + features[:4] + opinions
    v = Validator()
    web_articles = [article for article in articles if v.validate(article, ARTICLE_SCHEMA)]
    _log_validation_error_message(v.errors)
    return web_articles


def fetch_web_api():
    res = requests.get(config.WEBAPI, headers={'Content-Type': 'application/json',
                                               'Cache-Control': 'no-store',
                                               'Pragma': 'no-cache'})
    logger.info('web fetched: {}'.format(datetime.today().strftime('%Y/%m/%d %H:%M')))
    v = validator()
    v.validate(res.json(), web_blocks_schema)
    _log_validation_error_message(v.errors)
    articles = [article for block in res.json()['collectionblocks'] for article in block.get('items') if v.validate(article, web_article_schema)]
    _log_validation_error_message(v.errors)
    return _extract_web_articles(articles)


def fetch_app_articles():
    # res = wait_render(config.APP)
    res = requests.get(config.APP, headers={'Content-Type': 'application/json',
                                            'Cache-Control': 'no-store',
                                            'Pragma': 'no-cache'})
    logger.info('app fetched: {}'.format(datetime.today().strftime('%Y/%m/%d %H:%M')))
    v = Validator()
    v.validate(res.json(), APP_BLOCKS_SCHEMA)
    _log_validation_error_message(v.errors)
    articles = [story for story in res.json()['stories'] if v.validate(story, APP_STORY_SCHEMA) and story['title'] not in ['Editor\'s Picks', 'Opinion']]
    _log_validation_error_message(v.errors)
    return _scraping_app_articles(articles)


def job():
    web_articles = fetch_web_articles()
    # wait for sync
    time.sleep(330)
    app_articles = fetch_app_articles()
    validate(web_articles, app_articles)


def main():
    # schedule.every(6).minutes.do(job)
    schedule.every(30).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
