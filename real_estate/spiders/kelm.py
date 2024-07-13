import math
import re

import scrapy
from scrapy.loader import ItemLoader

from real_estate.items import KelmItem


class KelmSpider(scrapy.Spider):
    name = "kelm"
    allowed_domains = ["kelm-immobilien.de"]
    start_urls = ["https://kelm-immobilien.de/immobilien"]

    def parse(self, response):
        total_pages_container = response.css(
            "button.immomakler-submit.btn.btn-primary::text"
        ).getall()[1]
        try:
            total_items = int(re.findall(r"\d+", total_pages_container)[0])
        except TypeError:
            last_page = 1
        else:
            # defining actual paging number for loading paginated content
            last_page = int(math.ceil(total_items / 9))

        yield scrapy.Request(
            url=self.start_urls[0] + f"/page/{last_page}/",
            callback=self.parse_all_links
        )

    def parse_all_links(self, response):
        real_estate_links = response.css("h3.property-title>a::attr(href)").getall()
        yield from response.follow_all(real_estate_links, callback=self.parse_details)

    @staticmethod
    def parse_details(response):
        """ Parses detailed property paige. """
        item = ItemLoader(item=KelmItem(), selector=response)

        item.add_value("url", response.request.url)
        item.add_css("title", "h1.property-title")
        item.add_css("status", "li.data-vermietet>.row>div.dd")
        item.add_css("photos", "#immomakler-galleria>a::attr(href)")
        item.add_css("phone_number", "div.row.tel>div.dd>a")
        item.add_css("email", "div.row.email>div.dd>a")
        item.add_css("type", "li.list-group-item>.price>.dt")
        # checks a 'type' field value to use correct selector depends on 'type' output.
        match item.get_output_value("type"):
            case "purchase":
                item.add_css("price", "li.data-kaufpreis>.row>div.dd")
            case "rent":
                item.add_css("price", "li.data-kaltmiete>.row>div.dd")
            case _:
                item.add_value("price", None)
        item.add_css("description", "div.panel-body>p")

        yield item.load_item()
