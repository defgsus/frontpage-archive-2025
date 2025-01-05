from typing import Optional

import bs4

from ...scraper import Scraper


class Welt(Scraper):
    ID = "welt.de"
    URL = "https://www.welt.de"
    SUB_URLS = [
        ("index", URL),
        ("plus", URL + "/weltplus/"),
        ("newsticker", URL + "/newsticker/"),

        ("politik", URL + "/politik/"),
        ("wirtschaft", URL + "/wirtschaft/"),
        ("sport", URL + "/sport/"),
        ("panorama", URL + "/vermischtes/"),
        ("wissen", URL + "/wissenschaft/"),
        ("kultur", URL + "/kultur/"),
        ("meinung", URL + "/debatte/"),
        ("geschichte", URL + "/geschichte/"),
        ("reise", URL + "/reise/"),
        ("food", URL + "/food/"),
        ("regional", URL + "/regionales/"),
        ("sonderthemen", URL + "/sonderthemen/"),
    ]

    def find_headline(self, tag: bs4.Tag) -> Optional[bs4.Tag]:
        h = tag.find("h4")
        if h:
            return h.find("a")

    def patch_article(self, article: dict, tag: bs4.BeautifulSoup):
        article.update({
            "topic": self.strip(tag.find("h4").find("span", lambda c: "topic" in c)),
            "author": self.strip(tag.find("footer")),
        })
