import locale
import re
from enum import Enum


class TypeOption(str, Enum):
    """ Describing real estate offer type. """
    RENT = "kaltmiete"
    PURCHASE = "kaufpreis"


def offer_type_parser(options: list) -> str | None:
    """ Returns a real estate's offer type depends on property description
    :param: options: list of offer type related words
    :type: options
    :returns: ``str`` if matches with Enum options or None otherwise.
    """
    lowered_options = [option.lower() for option in options]
    if TypeOption.RENT in lowered_options:
        return "rent"
    elif TypeOption.PURCHASE in lowered_options:
        return "purchase"
    else:
        return None


def price_formatting(raw_price: str) -> str:
    """ Removes symbols which not a part of a price numeric value.
    :param: raw_price:
    :returns: price formatted str
    """
    numeric_price = re.sub(r'[^\d,.]', '', raw_price)
    return numeric_price


def description_organize(topics: list) -> str:
    """ Retrieves array of description's topics
    and merges all in one summary description """
    stripped_topics = []
    for topic in topics:
        # stripping and removing whitespaces and new line characters.
        updated_string = topic.replace("\n", "").strip()
        stripped_topics.append(updated_string)
    return " ".join(stripped_topics)
