# Scrapy settings for facms project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'facms'

SPIDER_MODULES = ['facms.spiders']
NEWSPIDER_MODULE = 'facms.spiders'

USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Mobile Safari/537.36'
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

# Maximum number of concurrent items (per response) to process in parallel in item pipelines. (default: 100)
# CONCURRENT_ITEMS = 100

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 10
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 0

# Disable cookies (enabled by default)
COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable Feeds export (csv, json, jl, etc..)
# FEEDS = {
#     'articles.csv': {
#         'format': 'csv',
#         'fields': ['key', 'title', 'author', 'kind', 'tag', 'section', 'date']
#     }
# }

# Custom Contracts (an integrated way of testing your spiders)
# SPIDER_CONTRACTS = {
#   'myproject.contracts.ResponseCheck': 10,
#   'myproject.contracts.ItemValidate': 10,
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# See https://doc.scrapy.org/en/latest/topics/settings.html#std-setting-SPIDER_MIDDLEWARES_BASE
#SPIDER_MIDDLEWARES = {
#    'facms.middlewares.facmsSpiderMiddleware': 543,
#    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None, # disable the default setting
#}

# use 'scrapy.pqueues.ScrapyPriorityQueue' by default for singl domain crawl
# use 'scrapy.pqueues.DownloaderAwarePriorityQueue' for crawling many different domains in parallel
# SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# See https://doc.scrapy.org/en/latest/topics/settings.html#std-setting-DOWNLOADER_MIDDLEWARES_BASE
#DOWNLOADER_MIDDLEWARES = {
#    'facms.middlewares.facmsDownloaderMiddleware': 543,
#    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # disable the default setting
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
#    'facms.pipelines.SpreadsheetPipeline': 300,
   'facms.pipelines.DatabasePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 12
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# It is not secure to use telnet console via public networks,
# as telnet doesn’t provide any transport-layer security.
# Having username/password authentication doesn’t change that.
# Intended usage is connecting to a running Scrapy spider locally (spider process and telnet client are on the same machine)
# or over a secure connection (VPN, SSH tunnel).
# TELNETCONSOLE_ENABLED = True
# TELNETCONSOLE_USERNAME = 'scrapy'
# TELNETCONSOLE_PASSWORD = 'scrapy'
