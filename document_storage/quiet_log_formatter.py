from scrapy import logformatter

class QuietLogFormatter(logformatter.LogFormatter):
    # Suppress printing of items after being scraped.
    # Enable printing again by setting LOG_SCRAPED_ITEMS to True in the spider
    def scraped(self, item, response, spider):
        return (
            super().scraped(item, response, spider)
            if spider.settings.getbool("LOG_SCRAPED_ITEMS")
            else None
        )
