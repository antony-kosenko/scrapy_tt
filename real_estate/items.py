import locale

import scrapy

from itemloaders.processors import Compose, MapCompose, TakeFirst
from w3lib.html import remove_tags

from real_estate.utils import offer_type_parser, price_formatting, description_organize


locale.setlocale(locale.LC_NUMERIC, "de_DE")


class KelmItem(scrapy.Item):
    """ Representation of real estate objects parsed from Kelm domain. """
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    status = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    photos = scrapy.Field()
    type = scrapy.Field(
        input_processor=Compose(
            MapCompose(remove_tags),
            offer_type_parser
        ), output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(
            remove_tags,
            price_formatting,
            locale.atof
        ),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=Compose(
            MapCompose(remove_tags),
            description_organize
        ),
        output_processor=TakeFirst()
    )
    phone_number = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst()
    )
    email = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst()
    )
