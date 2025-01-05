from typing import Generator
from ...scraper import Scraper


class Compact(Scraper):
    ID = "compact-online.de"
    URL = "https://www.compact-online.de/"
    SUB_URLS = [
        ("index", URL),

        ("plus", URL + "plus/"),
        ("aktuell", URL + "compact-aktuell/"),
        ("tv", "https://tv.compact-online.de/"),
    ]

    def iter_articles(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        soup = self.to_soup(content)
        for tag in soup.find_all("div", {"class": "content"}):
            if not (tag.text and tag.text.strip()):
                continue

            yield self.create_article_dict(
                title=self.strip(tag.find("div", {"class": "post-meta"})),
                teaser=self.strip(tag.find("div", {"class": "excerpt"}))
            )
