from typing import Generator, Tuple

from ...scraper import Scraper


class FrankfurterRundschau(Scraper):
    ID = "fr.de"
    URL = "https://www.fr.de/"
    SUB_URLS = [
        ("index.html", URL),
        ("politik.html", URL + "politik/"),
        ("meinung.html", URL + "meinung/"),
        ("eintracht-frankfurt.html", URL + "eintracht-frankfurt/"),
        ("frankfurt.html", URL + "frankfurt/"),
        ("wissen.html", URL + "wissen/"),
        ("panorama.html", URL + "panorama/"),
    ]

    def iter_articles(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        """
        Override this to extract article data from each scraped file.

        Base implementation looks for common <article> tag structures
        """
        soup = self.to_soup(content)
        for tag in soup.find_all("div", {"class": "id-Teaser-el-content"}):
            if not (tag.text and tag.text.strip()):
                continue

            headline = tag.find("h3") or tag.find("h2")
            if not headline:
                continue

            article = self.create_article_dict(
                title=self.strip(headline),
                teaser=self.strip(tag.find("p")),
            )

            a = tag.parent.find("a")
            if a and a.get("href"):
                article["url"] = self.url_join(url, a["href"])

            image = tag.parent.find("img")
            if image and image.get("src"):
                article["image_url"] = image["src"]
                if image.get("alt"):
                    article["image_title"] = self.strip(image["alt"])

            author = tag.parent.find("p", {"class": "id-Teaser-el-content-author"})
            author = self.strip(author)
            if author:
                if author.lower().startswith("von "):
                    author = author[4:]
                article["author"] = author

            yield article

