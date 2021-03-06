# -*- coding: utf-8 -*-
from fake_useragent import UserAgent

# Scrapy settings for misinformation project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'misinformation'

SPIDER_MODULES = ['misinformation.spiders']
NEWSPIDER_MODULE = 'misinformation.spiders'

FEED_FORMAT = 'jsonlines'
LOG_LEVEL = 'INFO'

# Set maximum length of URL to crawl to match the worst case maximum length that
# can be uniquely indexed by Azure SQL server.
# The maximum length of a nonclustered index is 1700 bytes and each character in
# a unicode storing NVCHAR column can require two bytes of storage
URLLENGTH_LIMIT = 850

# The polite thing to do is to crawl responsibly by identifying ourselves in the user-agent string.
# However, we get 403 forbidden errors with some sites when using the scrapy default user-agent
# Here we fix our user agent as the latest one for Chrome for reproducibility (rather than generate a random
# one based on real world usage distribution).
USER_AGENT = UserAgent().chrome

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Ensure exporters write unicode rather than ASCII encoded output
FEED_EXPORT_ENCODING = 'utf-8'

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'misinformation.middlewares.MisinformationSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'misinformation.middlewares.ButtonPressMiddleware': 400,
    'misinformation.middlewares.CloudFlareMiddleware': 500,
    'misinformation.middlewares.DelayedRetryMiddleware': 600
}
# This does not work as all the code is Python 2 and I haven't managed to port it to Python 3
# DOWNLOADER_MIDDLEWARES = {'warcmiddleware.WarcMiddleware': 820}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.closespider.CloseSpider': 500
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'misinformation.pipelines.ArticleBlobStorageExporter': 300,
    'misinformation.pipelines.ArticleJsonFileExporter': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# This does not work as scrapy now uses HTTP1.1, which uses a higher-level Agent class from Twisted
# See https://groups.google.com/forum/#!topic/scrapy-users/pKDXCJlFJaw
# DOWNLOADER_HTTPCLIENTFACTORY = 'warcclientfactory.WarcHTTPClientFactory'
