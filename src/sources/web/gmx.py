from typing import Generator

from ...scraper import Scraper


class GMX(Scraper):
    ID = "gmx.net"
    URL = "https://www.gmx.net/"
    SUB_URLS = [
        ("index", URL),
        ("news", URL + "magazine/"),
        ("sport", URL + "magazine/sport/"),
        ("unterhaltung", URL + "magazine/unterhaltung/"),
        ("ratgeber", URL + "magazine/ratgeber/"),
        ("auto", URL + "magazine/auto/"),
    ]

    def iter_articles(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        soup = self.to_soup(content)
        for tag in soup.find_all("a"):
            if tag.get("data-component") != "teaser":
                content

            if not (tag.text and tag.text.strip()):
                continue

            headline = self.find_headline(tag)
            headline = self.strip(headline)
            if not headline:
                continue

            article = self.create_article_dict(
                title=headline,
                teaser=self.strip(tag.find("p")) or self.strip(tag.find("section")),
            )

            if tag.get("href"):
                article["url"] = self.url_join(url, tag["href"])

            image = tag.find("img")
            if image and image.get("src"):
                article["image_url"] = image["src"]
                article["image_title"] = self.strip(
                    image.get("alt") or image.get("title")
                )

            self.patch_article(article, tag)

            yield article
