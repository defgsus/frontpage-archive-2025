from typing import Generator, Tuple

from ...scraper import Scraper


class FrankfurterAllgemeine(Scraper):
    ID = "faz.net"
    URL = "https://www.faz.net/"
    SUB_URLS = [
        ("index", URL + "aktuell/"),
        ("politik", URL + "aktuell/politik/"),
        ("bundestagswahl", URL + "aktuell/politik/bundestagswahl/"),
        ("wirtschaft", URL + "aktuell/wirtschaft/"),
        ("finanzen", URL + "aktuell/finanzen/"),
        ("feuilleton", URL + "aktuell/feuilleton/"),
        ("karriere", URL + "aktuell/karriere-hochschule/"),
        ("sport", URL + "aktuell/sport/"),
        ("gesellschaft", URL + "aktuell/gesellschaft/"),
        ("stil", URL + "aktuell/stil/"),
        ("rhein-main", URL + "aktuell/rhein-main/"),
        ("technik", URL + "aktuell/technik-motor/"),
        ("wissen", URL + "aktuell/wissen/"),
        ("reise", URL + "aktuell/reise/"),
    ]

    def iter_articles(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        soup = self.to_soup(content)
        for tag in soup.find_all("div", {"class": "teaser-object"}):
            if not (tag.text and tag.text.strip()):
                continue

            headline = self.find_headline(tag)
            headline = self.strip(headline)
            if not headline:
                continue

            article = self.create_article_dict(
                title=headline,
                teaser=(
                    self.strip(tag.find("div", {"class": "p2-teaser"}))
                ),
            )

            a = tag.find("a")
            if a and a.get("href"):
                article["url"] = self.url_join(url, a["href"])

            image = tag.find("img")
            if image and image.get("src"):
                article["image_url"] = image["src"]
                article["image_title"] = self.strip(
                    image.get("alt") or image.get("title")
                )

            self.patch_article(article, tag)

            yield article
