import math
import re
import locale
import scrapy


locale.setlocale(locale.LC_NUMERIC, "de_DE")


class KelmSpider(scrapy.Spider):
    name = "kelm"
    allowed_domains = ["kelm-immobilien.de"]
    start_urls = ["https://kelm-immobilien.de/immobilien"]

    def parse(self, response):
        total_items_container = response.css(
            "button.immomakler-submit.btn.btn-primary::text"
        ).getall()[1]
        try:
            total_items = int(re.findall(r"\d+", total_items_container)[0])
        except TypeError:
            total_items = None
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

    def parse_details(self, response):
        rent, buy = ("Kaltmiete", "Kaufpreis")
        item_offer_type = response.css("li.list-group-item>.price>.dt::text").getall()
        if rent in item_offer_type:
            offer_type = "rent"
            raw_price = response.css("li.data-kaltmiete>.row>div.dd::text").get()
        elif buy in item_offer_type:
            offer_type = "purchase"
            raw_price = response.css("li.data-kaufpreis>.row>div.dd::text").get()
        else:
            offer_type = None
            raw_price = None
        price = re.sub(r'[^\d,.]', '', raw_price)
        description_container = response.css("div.panel-body>p::text").getall()

        yield {
            "url": response.request.url,
            "title": response.css("h1.property-title::text").get(),
            "status": response.css("li.data-vermietet>.row>div.dd::text").get(),
            "photos": response.css("#immomakler-galleria>a::attr(href)").getall(),
            "type": offer_type,
            "price": locale.atof(price),
            "description": " ".join(description_container),
            "phone_number": response.css("div.row.tel>div.dd>a::text").get(),
            "email": response.css("div.row.email>div.dd>a::text").get()
        }
