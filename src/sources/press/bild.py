from typing import Generator, Tuple, Optional

import bs4

from ...scraper import Scraper


class Bild(Scraper):
    ID = "bild.de"
    URL = "https://www.bild.de"

    SUB_LINK_NAMES = [
        "News",
        "Politik",
        "Regio",
        "Unterhaltung",
        "Sport",
        "Fussball",
        "Lifestyle",
        "Ratgeber",
        "Auto",
        "Digital",
        "Inland",
        "Ausland",
        "Mystery",
        "Ein Herz für Kinder",
        "Kommentare und Kolumnen",
        "Stars",
        "Erotik",
        "Kino",
        "TV",
        "Reise",
        "Gesundheit",
        "Geld & Wirtschaft",
        "Wirtschaft",
    ]

    def find_headline(self, tag: bs4.Tag) -> Optional[bs4.Tag]:
        return super().find_headline(tag) or tag.find("div", {"class": "teaser__title"})
