from typing import Generator

from ...scraper import Scraper


class Sueddeutsche(Scraper):
    ID = "sueddeutsche.de"
    URL = "https://www.sueddeutsche.de/"
    SUB_URLS = [
        ("index", URL),
        ("plus", "https://plus.sueddeutsche.de/"),
        ("politik", URL + "politik"),
        ("wirtschaft", URL + "wirtschaft"),
        ("meinung", URL + "meinung"),
        ("panorama", URL + "panorama"),
        ("sport", URL + "sport"),
    ]

    def iter_articles(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        soup = self.to_soup(content)
        for tag in soup.find_all("a", {"class": "sz-teaser"}):

            article = self.create_article_dict(
                title=self.strip(tag.find("h3") or tag.find("h2") or tag.find("h1")),
                teaser=self.strip(tag.find("p")),
                url=self.url_join(url, tag["href"]),
            )

            author = self.strip(tag.find("p", lambda t: "author" in t))
            if author:
                if author.startswith("Von "):
                    author = author[4:]
                article["author"] = author

            image = tag.find("img")
            if image:
                srcset = image.get("data-srcset") or image.get("srcset")
                if not srcset:
                    srcset = (tag.find("source") or {}).get("data-srcset")
                if srcset:
                    article["image_url"] = srcset.split("?v", 1)[0]
                article["image_title"] = self.strip(image.get("alt") or image.get("title"))

            yield article
