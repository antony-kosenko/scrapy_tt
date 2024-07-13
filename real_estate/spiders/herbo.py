import time
from typing import Collection

import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from real_estate.items import HerboItem


def parse_object_url(url_with_id: str) -> str:
    """ Takes current url contains id and returns complete
    url contains object detailed data. """
    base_url = "https://bostad.herbo.se/HSS/Object/ObjectDetailsPrint.aspx?objectguid="
    builded_url = base_url + url_with_id.split("objectguid=")[-1]
    return builded_url


class HerboSpider(scrapy.Spider):
    name = "herbo"
    # root url path being incremented for subject link build
    ROOT_URL = "https://bostad.herbo.se/HSS/Object/"

    def start_requests(self):
        url = ("https://bostad.herbo.se/HSS/Object/"
               "ObjectSearchResult.aspx?objectgroup=1&action=search")
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response) -> SeleniumRequest:
        # binds property links css selector for further use
        links_selector = "a[id$='ObjectDetailsUrl']"
        # retrieving all properties' links
        properties_link = response.css(links_selector + "::attr(href)").getall()
        # building absolute url path for property link.
        built_links = [(self.ROOT_URL + link) for link in properties_link]

        # pagination container
        total_pages = int(response.css("span[id$='lblNoOfPages']::text").get())
        current_page = int(response.css("span[id$='lblCurrPage']::text").get())
        if total_pages > 1:
            driver: WebDriver = response.request.meta['driver']

            next_page = driver.find_element(
                By.CSS_SELECTOR,
                "a[id$='btnNavNext']"
            )
            while current_page < total_pages:
                next_page.click()
                more_links = driver.find_elements(
                    By.CSS_SELECTOR,
                    links_selector
                )
                links_built = [link.get_attribute("href") for link in more_links]
                built_links.extend(links_built)
                current_page += 1
        for link in built_links:
            yield SeleniumRequest(
                url=link,
                callback=self.parse_base_data,
            )

    def parse_base_data(self, response) -> SeleniumRequest:
        """ Parses popup frame windows which requires a click. """
        # getting current browser driver
        driver: WebDriver = response.request.meta['driver']
        driver.get(response.request.url)
        WebDriverWait(driver, 20).until(
            EC.url_to_be(response.request.url)
        )
        driver.maximize_window()
        # pulling photos' links
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[id$='imgBig2']"))
        ).click()
        photos_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "img.fancybox-image"
        )
        # arranging photos' urls list
        photos_urls = [url.get_attribute("src") for url in photos_elements]
        # closing images slide container
        close_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.fancybox-button--close"
        )
        action = ActionChains(driver)
        action.move_to_element(close_button).click(close_button).perform()
        yield SeleniumRequest(
            url=parse_object_url(response.request.url),
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


