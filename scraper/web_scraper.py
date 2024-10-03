import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class WebsiteSpider(CrawlSpider):
    name = 'website_spider'

    def __init__(self, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]
        self.allowed_domains = [kwargs.get('allowed_domain')]

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        yield {
            'url': response.url,
            'title': response.css('h1::text').get(),
            'content': ' '.join(response.css('p::text').getall())
        }

def main():
    start_url = input("Enter the starting URL: ").strip()
    allowed_domain = input("Enter the allowed domain: ").strip()

    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    })

    process.crawl(WebsiteSpider, start_url=start_url, allowed_domain=allowed_domain)
    process.start()

if __name__ == "__main__":
    main()