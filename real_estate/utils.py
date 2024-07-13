import re
from enum import Enum
from typing import Collection


class TypeOption(str, Enum):
    """ Describing real estate valid offer type. """
    RENT = "kaltmiete"
    PURCHASE = "kaufpreis"


def offer_type_parser(options: list) -> str | None:
    """ Returns a real estate's offer type depends on property description
    :param list options: contains the words found in description
           related to type of property.
    :returns: offer type ``str`` representation if matches with Enum
           options or None otherwise.
    """
    # lowering input values
    lowered_options = [option.lower() for option in options]
    if TypeOption.RENT in lowered_options:
        return "rent"
    elif TypeOption.PURCHASE in lowered_options:
        return "purchase"
    else:
        return None


def price_formatting(raw_price: str) -> str:
    """ Removes symbols which not a part of a price numeric value.
    :param str raw_price: input price parameter as string which
           may contains alphabetical and other unexpected symbols.
    :returns: price formatted ``str``.
    """
    numeric_price = re.sub(r'[^\d,.]', '', raw_price)
    return numeric_price


def description_organize(topics: Collection) -> str:
    """ Retrieves array of description's topics
    and merges all in one summary description """
    stripped_topics = []
    for topic in topics:
        # stripping and removing whitespaces and new line characters.
        try:
            updated_string = topic.replace("\n", "").strip()
        except (AttributeError, AttributeError):
            pass
        else:
            stripped_topics.append(updated_string)
            return " ".join(stripped_topics)


class HerboProcessors:
    """ Implements different methods for field values processing
    Herbo specific domain"""

    @staticmethod
    def build_avaliability_status(value: str) -> str:
        """ Returns an availability date with comment."""
        return f"Avaliable form {value}"
