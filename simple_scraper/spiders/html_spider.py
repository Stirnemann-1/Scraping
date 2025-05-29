# simple_scraper/simple_scraper/spiders/html_spider.py
import scrapy

class HtmlSpider(scrapy.Spider):
    name = "html_scraper"

    def __init__(self, url_to_scrape=None, *args, **kwargs):
        super(HtmlSpider, self).__init__(*args, **kwargs)
        if url_to_scrape:
            self.start_urls = [url_to_scrape]
        else:
            self.start_urls = []
        self.results_list = kwargs.get('results_list', None)

    def parse(self, response):
        scraped_data = {
            'url': response.url,
            'html_content': response.text
        }
        if self.results_list is not None:
            self.results_list.append(scraped_data)
