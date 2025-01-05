import bs4

from ...scraper import Scraper


class Heise(Scraper):
    ID = "heise.de"
    URL = "https://www.heise.de/"
    SUB_URLS = [
        ("index", URL),
        ("it", URL + "newsticker/it/"),
        ("wissen", URL + "newsticker/wissen/"),
        ("mobiles", URL + "newsticker/mobiles/"),
        ("security", URL + "security/"),
        ("entertainment", URL + "newsticker/entertainment/"),
        ("netzpolitik", URL + "newsticker/netzpolitik/"),
        ("wirtschaft", URL + "newsticker/wirtschaft/"),
        ("journal", URL + "newsticker/journal/"),
        ("newsticker", URL + "newsticker/"),
        ("plus", URL + "plus/"),
        ("telepolis", URL + "tp/"),
    ]

    def patch_article(self, article: dict, tag: bs4.BeautifulSoup):
        author = tag.find("li", {"class": "has-author"})
        article["author"] = self.strip(author)
