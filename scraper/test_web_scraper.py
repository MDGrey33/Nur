import os
import json
from scrapy.crawler import CrawlerProcess
from web_scraper import WebsiteSpider

def test_web_scraper():
    # Set up the test environment
    start_url = "http://books.toscrape.com/"
    allowed_domain = "books.toscrape.com"
    output_file = "test_output.json"

    # Run the scraper
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': output_file
    })
    process.crawl(WebsiteSpider, start_url=start_url, allowed_domain=allowed_domain)
    process.start()

    # Check if the output file exists
    assert os.path.exists(output_file), "Output file not generated"

    # Load the scraped data from the output file
    with open(output_file, 'r') as file:
        scraped_data = json.load(file)

    # Perform assertions on the scraped data
    assert len(scraped_data) > 0, "No data scraped"
    assert all(key in scraped_data[0] for key in ['url', 'title', 'content']), "Missing required fields in scraped data"

    # Clean up the test output file
    os.remove(output_file)

    print("Web scraper test passed!")

if __name__ == "__main__":
    test_web_scraper()