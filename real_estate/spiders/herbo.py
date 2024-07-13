import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from real_estate.items import HerboItem


class HerboSpider(scrapy.Spider):
    name = "herbo"
    allowed_domain = ["bostad.herbo.se"]
    start_urls = ["https://bostad.herbo.se/HSS/Object/ObjectSearchResult.aspx?objectgroup=1&action=search"]
    # root url path being incremented for subject link build
    ROOT_URL = "https://bostad.herbo.se/HSS/Object/"

    def parse(self, response) -> SeleniumRequest:
        # binds property links css selector for further use
        links_selector = ("table.gridlist>[class^=listitem]>"
                          "td:nth-child(2n)>a::attr(href)")
        # retrieving all properties' links
        properties_link = response.css(links_selector).getall()
        # building absolute url path for property link.
        built_links = [(self.ROOT_URL + link) for link in properties_link]
        for link in built_links:
            yield SeleniumRequest(
                url=link,
                callback=self.parse_print_box,
            )

    def parse_print_box(self, response) -> SeleniumRequest:
        """ Parses popup frame windows which requires a click. """
        # getting current browser driver
        driver: WebDriver = response.request.meta['driver']
        driver.set_window_size(1440, 900)
        # pulling photos' links
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.image-big"))
        ).click()
        photos_elements = driver.find_elements(By.CSS_SELECTOR, "img.fancybox-image")
        # arranging photos' urls list
        photos_urls = [url.get_attribute("src") for url in photos_elements]
        # closing images slide container
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fancybox-button--close"))
        ).click()
        # looking for print button and pressing
        driver.find_element(By.CSS_SELECTOR, "span.btn_facts").click()
        extended_data_url = driver.find_element(
            By.CSS_SELECTOR, "iframe.fancybox-iframe"
        ).get_attribute("src")
        return SeleniumRequest(
            url=extended_data_url,
            callback=self.parse_details,
            cb_kwargs={"pictures": photos_urls}
        )

    def parse_details(self, response, pictures: list):
        """ Parsing detailed data contained in property 'print' button. """
        obj_description = response.css("span[id$='lblDescription']::text").get()
        obj_extra_data = response.css("span[id$='lblExtra']::text").get()
        # initiating herbo properties item loader.
        item = ItemLoader(item=HerboItem(), selector=response)

        item.add_value("url", response.request.url)
        item.add_css("title", "li.address_name")
        item.add_css("status", "#ctl00_Col1_lblDateAvailable::text")
        item.add_value("pictures", pictures)
        item.add_value(
            "price",
            "tbody>tr[id$='Cost']>td[class$='content']>span::text"
        )
        item.add_value("description", (obj_description, obj_extra_data))
        item.add_css("phone_number", "span[id$='lblCompanyPhone']")
        # loading item
        yield item.load_item()


