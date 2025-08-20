from datetime import datetime
import locale

from document_storage.document_storage import DocumentStorage
from items import ICResponseItem
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from settings import DOMAIN, IC_PATH, NUMBER_RESPONSE_PAGES
from utils.error_log import ErrorLog

class ICResponsesSpider(Spider):
    name = 'internet-consultatie-responses'
    spider_type = 'items'
    download_delay = 1
    base_url = f'{DOMAIN}{IC_PATH}/reacties/datum/'

    start_urls = [f'{base_url}{NUMBER_RESPONSE_PAGES}']

    def __init__(self):
      locale.setlocale(locale.LC_TIME, 'nl_NL')
      self.document_storage = DocumentStorage()
      self.last_response_number = self.document_storage.get_last_response_number()

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        # settings.set("LOG_SCRAPED_ITEMS", True, priority="spider")
        # For response_number to make sense: process 1 by 1
        settings.set("CONCURRENT_REQUESTS", 1)
        settings.set("DEPTH_PRIORITY", 1)
        settings.set("SCHEDULER_DISK_QUEUE", "scrapy.squeues.PickleFifoDiskQueue")
        settings.set("SCHEDULER_MEMORY_QUEUE", "scrapy.squeues.FifoMemoryQueue")

    def log_error(self, message):
        ErrorLog().write(message)
        
    def parse(self, response):
        if response.status == 404:
            message = "Spider: received 404 response"
            self.log_error(message)
            raise CloseSpider(message)

        result_list = response.css("div.result--list ul li")
        if len(result_list) == 0:
            message = "Spider: no more results found"
            self.log_error(message)
            raise CloseSpider(message)

        for item in reversed(result_list):
          link = item.css('a').attrib["href"]
          response_uuid = link.split('/')[-1]
          if self.document_storage.has_been_archived(response_uuid):
              continue

          name = item.css('a::text').get()
          place, time_string = item.css('p::text').get().split("|")
          # Extract date and time here, because time is not present on details page
          timestamp = None
          try:
             timestamp = datetime.strptime(time_string.strip(), '%d %B %Y (%H:%M)')
          except Exception as e:
              self.log_error(f"{link}: error parsing timestamp {time_string}: {e}")
              raise e
          
          url = f'{DOMAIN}{link}'
          response_number = self.last_response_number + 1
          yield Request(url, callback=self.get_ic_response_contents, meta={
             'name': name,
             'place': place,
             'timestamp': timestamp,
             'url': url,
             'response_number': response_number
          })
          self.last_response_number = response_number

        previous_page = self.get_previous_page(response.url)
        if previous_page:
            yield Request(previous_page)


    def get_ic_response_contents(self, response):
        # A response can contain both text and an attachment
        meta = response.meta
        item = ICResponseItem()
        item['name'] = meta['name']
        item['place'] = meta['place']
        item['timestamp'] = meta['timestamp']
        item['url'] = meta['url']
        item['response_number'] = meta['response_number']

        # Add text
        text = ' '.join(response.css('#content blockquote > div::text').getall())
        item['text'] = text

        # Attachments (we can for more, but it seems you can only upload 1 attachment when responding)
        item['attachments'] = []
        for link in response.css('ul.result--actions a'):
            url = f"{DOMAIN}{link.attrib['href']}"
            item['attachments'].append(url)

        yield item

    def get_previous_page(self, url):
        # url is of the form 'https://www.internetconsultatie.nl/terrorismeverheerlijking/reacties/datum/N'
        # Determine N and decrease by 1
        page_number = None
        page_number_string = url.split('/')[-1]
        try:
           page_number = int(page_number_string) - 1
           if page_number == 0:
               return
        except ValueError as e:
           return

        print(f"\n\nNew page number: {page_number}")
        return f'{self.base_url}{page_number}'
