from datetime import datetime
import locale

from items import ICResponseItem
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from utils.error_log import ErrorLog

class ICResponsesSpider(Spider):
    name = 'internet-consultatie-responses'
    spider_type = 'items'
    download_delay = 1
    domain = 'https://www.internetconsultatie.nl'
    base_url = f'{domain}/terrorismeverheerlijking/reacties/datum/'
    start_page = 1

    start_urls = [f'{base_url}{start_page}']

    def __init__(self):
      locale.setlocale(locale.LC_TIME, 'nl_NL')

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        # settings.set("LOG_SCRAPED_ITEMS", True, priority="spider")

    def parse(self, response):
        if response.status == 404:
            message = "Spider: received 404 response"
            ErrorLog().write(message)
            raise CloseSpider(message)

        result_list = response.css("div.result--list ul li")
        if len(result_list) == 0:
            message = "Spider: no more results found"
            ErrorLog().write(message)
            raise CloseSpider(message)

        for item in result_list:
          # Extract date and time here, because time is not present on details page
          name = item.css('a::text').get()
          link = item.css('a').attrib["href"]
          place, time_string = item.css('p::text').get().split("|")
          timestamp = None
          try:
             timestamp = datetime.strptime(time_string.strip(), '%d %B %Y (%H:%M)')
          except Exception as e:
              ErrorLog().write(f"{link}: error parsing timestamp {time_string}: {e}")
              raise e
          
          url = f'{self.domain}{link}'
          yield Request(url, callback=self.get_ic_response_contents, meta={
             'name': name,
             'place': place,
             'timestamp': timestamp,
             'url': url
          })

        next_page = self.get_next_page(response.url)
        if next_page:
            yield Request(next_page)


    def get_ic_response_contents(self, response):
        meta = response.meta
        item = ICResponseItem()
        item['name'] = meta['name']
        item['place'] = meta['place']
        item['timestamp'] = meta['timestamp']
        item['url'] = meta['url']

        # Add text
        text = ' '.join(response.css('#content blockquote > div::text').getall())
        item['text'] = text

        # Attachments
        item['attachments'] = []
        for link in response.css('ul.result--actions a'):
            url = f"{self.domain}{link.attrib['href']}"
            item['attachments'].append(url)

        yield item

    def get_next_page(self, url):
        # url is of the form 'https://www.internetconsultatie.nl/terrorismeverheerlijking/reacties/datum/N'
        # Determine N and increase by 1
        page_number = None
        page_number_string = url.split('/')[-1]
        try:
           page_number = int(page_number_string) + 1
        except ValueError as e:
           return None
        print(f"\n\nNew page number: {page_number}")

        return f'{self.base_url}{page_number}'
