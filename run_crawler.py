import locale

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders.ICResponsesSpider import ICResponsesSpider

locale.setlocale(locale.LC_TIME, 'nl_NL')

process = CrawlerProcess(get_project_settings())
process.crawl(ICResponsesSpider)
process.start()
