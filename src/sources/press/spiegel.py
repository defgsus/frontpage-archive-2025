import re

import bs4

from ...scraper import Scraper


class Spiegel(Scraper):
    ID = "spiegel.de"
    URL = "https://www.spiegel.de/"
    SUB_URLS = [
        ("index", URL),
        ("schlagzeilen", URL + "schlagzeilen/"),
        ("plus", URL + "plus/"),
        ("coronavirus", URL + "thema/coronavirus/"),
        ("politik", URL + "politik/"),
        ("ausland", URL + "ausland/"),
        ("panorama", URL + "panorama/"),
        ("sport", URL + "sport/"),
        ("wirtschaft", URL + "wirtschaft/"),
        ("wissenschaft", URL + "wissenschaft/"),
        ("netzwelt", URL + "netzwelt/"),
        ("kultur", URL + "kultur/"),
        ("leben", URL + "thema/leben/"),
        ("karriere", URL + "karriere/"),
        ("geschichte", URL + "geschichte/"),
        ("auto", URL + "auto/"),
        ("tests", URL + "tests/"),
        ("deinspiegel", URL + "deinspiegel/"),
        ("audio", URL + "audio/"),
        ("video", URL + "video/"),
    ]

    _RE_TITLE_TIME = re.compile("Vor \d+ Min$")

    def patch_article(self, article: dict, tag: bs4.BeautifulSoup):
        if article["title"]:
            article["title"] = self._RE_TITLE_TIME.sub("", article["title"]).strip()

        section = tag.find("section")
        if section:
            spans = section.find_all("span")
            if spans and spans[-1].text:
                author = spans[-1].text.strip()
                if author.startswith("Von "):
                    article["author"] = author[4:]
