import bs4

from ...scraper import Scraper


class Volksstimme(Scraper):
    ID = "volksstimme.de"
    URL = "https://www.volksstimme.de/"
    SUB_URLS = [
        ("index", URL),

        ("sport", URL + "sport"),
        ("deutschland-und-welt", URL + "deutschland-und-welt"),
        ("panorama", URL + "panorama"),
        ("panorama", URL + "panorama"),
        ("panorama", URL + "panorama"),
        ("kultur", URL + "kultur"),
        ("leben", URL + "leben"),
        ("blaulicht", URL + "blaulicht"),
    ]

    def patch_article(self, article: dict, tag: bs4.BeautifulSoup):
        article["topic"] = self.strip(tag.find("h4"))
