from datetime import datetime
import scrapy

class ICResponseItem(scrapy.Item):
  name = scrapy.Field()
  place = scrapy.Field()
  timestamp = scrapy.Field()
  url = scrapy.Field()
  text = scrapy.Field()
  attachments = scrapy.Field()
  response_number = scrapy.Field()

  def get_response_uuid(self):
    return self['url'].split('/')[-1]

  def get_timestamp(self):
    timestamp = self['timestamp']
    if not timestamp: return

    return datetime.strftime(timestamp, "%d %B %Y (%H:%M)")
  
  def get_description(self):
    return f"Reactie van {self['name']}, {self['place']} op {self.get_timestamp()}"