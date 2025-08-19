from datetime import datetime
import scrapy

class ICResponseItem(scrapy.Item):
  name = scrapy.Field()
  place = scrapy.Field()
  timestamp = scrapy.Field()
  url = scrapy.Field()
  text = scrapy.Field()
  attachments = scrapy.Field()

  def get_filename(self):
    return self['url'].split('/')[-1]

  def get_timestamp(self):
    timestamp = self['timestamp']
    if not timestamp: return

    return datetime.strftime(timestamp, "%d %B %Y (%H:%M)")