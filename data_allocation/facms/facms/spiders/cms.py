import re
# import logging

from bs4 import BeautifulSoup as bs
from datetime import datetime
import scrapy
from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
# from scrapy.spiders import SitemapSpider
# from scrapy.loader import ItemLoader
from facms.items import FacmsItem
from facms.spiders import LOGIN, CMS_ID, CMS_PS, ARTICLE


class CmsSpider(CrawlSpider):
    # The spider name is how the spider is located (and instantiated) by Scrapy, so it must be unique
    name = 'facms'

    # These are attributes for BASIC authentication
    # http_user = 'someuser'
    # http_pass = 'somepass'

    # An optional list of strings containing domains that this spider is allowed to crawl
    domain = LOGIN.replace('https://', '').split('/').pop(0)
    allowed_domains = [domain]

    # A dictionary of settings that will be overridden from the project wide configuration when running this spider.
    # custom_settings = {}
    # self.settings['BOT_NAME']

    # This attribute is set by the from_crawler() class method after initializating the class,
    # and links to the Crawler object to which this spider instance is bound.
    # crawler = {}

    # Each Rule defines a certain behaviour for crawling the site.
    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).
    #     Rule(LinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),

    #     # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #     Rule(LinkExtractor(allow=('item\.php', )), callback='parse_item'),
    # )

    # This list will then be used by the default implementation of start_requests()
    # to create the initial requests for your spider
    start_urls = []

    # Instead of start_urls you can use start_requests() directly; to give data more structure
    # def start_requests(self):
    #     You can provide command line arguments with your spiders by "-a" option
    #     tag = getattr(self, 'tag', '')
    #     for url in urls:
    #         yield scrapy.Request('{}/{}'.format(url, tag), callback=self.parse)

    def __init__(self, *args, **kwargs):
        # diable INFO log
        # logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        # logger.setLevel(logging.WARNING)
        # super().__init__(*args, **kwargs)

        if not kwargs:
            self.start_urls.append(LOGIN)
        else:
            query = '&'.join([ '{k}={v}'.format(k=k, v=v) for k, v in kwargs.items()])
            self.start_urls.append('{}?{}'.format(LOGIN, query))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CmsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: {}'.format(spider.name))

    def parse(self, response):
        payload = {
            'log': CMS_ID,
            'pwd': CMS_PS,
            'wp-submit': 'Log In'
        }
        # request with the curl command
        # yield request = Request.from_curl(
        #     "curl 'http://quotes.toscrape.com/api/quotes?page=1' -H 'User-Agent: ..."
        # )

        # yield scrapy.Request(LOGIN,
        #                      method='GET',
        #                      body='',
        #                      encoding='utf-8',
        #                      priority=0,
        #                      dont_filter=False,
        #                      headers={},
        #                      cookies={'currency': 'USD', 'country': 'UY'},
        #                      cb_kwargs={'foo': 'bar'},
        #                      errback=self.errorback,
        #                      meta={'dont_merge_cookies': True},  # ignores cookie storage
        #                      callback=self.logged_in)

        # yield scrapy.http.JsonRequest(url='http://www.example.com/post/action', data=data)
        yield scrapy.FormRequest.from_response(
            response,
            formdata=payload,
            # dont_click=False,
            callback=self.logged_in
        )

    def errorback(self, failure):
        yield dict(foo=failure.request.cb_kwargs['foo'])

    def logged_in(self, response, foo=''):
        self.logger.info('Login: {}'.format(response.url))
        # response.status
        # response.headers
        # response.body
        # response.request
        # response.ip_address

        # for href in urls:
        #     yield response.follow(href, callback=self.parse)
        # yield from response.follow_all(urls, callback=seld.parse)
        yield scrapy.Request(ARTICLE,
                             callback=self.parse_article)

    def parse_article(self, response):
        self.logger.info('Parse Article: {}'.format(response.url))
        # l = ItemLoader(item=FacmsItem(), response=response)
        # l.add_xpath('key', '//td[@data-colname="Key"]')
        # l.add_value('title', 'Title')
        # return l.load_item()
        try:
            soup = bs(response.text, features='lxml')
            total = int(soup.find('span', attrs={'class': 'total-pages'}).text) + 1
            self.logger.info('{}'.format(total))
            urls = ['{}?paged={}'.format(ARTICLE, page) for page in range(1, 2)]
        except:
            from scrapy.shell import inspect_response
            inspect_response(response, self)
        yield from response.follow_all(urls, callback=self.scraping_article)

    def scraping_article(self, response):
        self.logger.info('Scraping Article: {}'.format(response.url))
        parser = bs(response.text, features='lxml')
        (keys, titles, authors, kinds, tags, sections, dates) = self._extract_article_meta(parser)
        for key, title, author, kind, tag, section, date in zip(keys, titles, authors, kinds, tags, sections, dates):
            yield self._insert_article({'key': key, 'title': title, 'author': author, 'kind': kind, 'tag': tag, 'section': section, 'date': date})

    def _extract_article_meta(self, parser):
        keys = [re.search('post=([0-9]*)', key.find('a').get('href'))[1]
            for key in parser.find_all('td', attrs={'data-colname': 'Title'})]
        titles = [title.find('a').text for title in parser.find_all('td', attrs={'data-colname': 'Title'})]
        authors = [author.text for author in parser.find_all('td', attrs={'data-colname': 'Author'})]
        kinds = [kind.text for kind in parser.find_all('td', attrs={'data-colname': 'Article Types'})]
        tags = ['+'.join([tag.text for tag in taglist.find_all('a')])
                for taglist in parser.find_all('td', attrs={'data-colname': 'Timeline Tags'})]
        sections = [section.text for section in parser.find_all('td', attrs={'data-colname': 'Sections'})]
        dates = [date.find('span').text for date in parser.find_all('td', attrs={'data-colname':'Date'})]
        return keys, titles, authors, kinds, tags, sections, dates

    def _insert_article(self, article):
        item = FacmsItem()
        item['key'] = article['key']
        item['title'] = article['title']
        item['author'] = article['author']
        item['kind'] = article['kind']
        item['tag'] = article['tag']
        item['section'] = article['section']
        item['date'] = article['date']
        return item
