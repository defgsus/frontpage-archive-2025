import re
import os
import sys
import glob
import json
import datetime
import traceback
import hashlib
import pickle
import urllib.parse
from pathlib import Path
from typing import Generator, Tuple, Union, Optional, List

import requests
import bs4

scraper_classes = dict()


class Scraper:

    ID: str = None      # must be filename compatible
    NAME: str = None    # leave None to copy ID
    URL: str = None

    # base implementation of iter_files() yields these urls
    #   defaults to [("index", URL)]
    SUB_URLS: List[Tuple[str, str]] = []

    # add names of links to follow on the first SUB_URLS page, like "Impressum"
    SUB_LINK_NAMES = []

    # set to True in abstract classes
    ABSTRACT: bool = False

    # request timeout in seconds
    REQUEST_TIMEOUT: float = 10
    # Set to false to run every request in individual session
    USE_SESSION: bool = True

    BASE_PATH: Path = Path(__file__).resolve().parent.parent / "docs" / "snapshots"
    CACHE_PATH: Path = Path(__file__).resolve().parent.parent / "cache"

    def __init_subclass__(cls, **kwargs):
        if not cls.ABSTRACT:

            if cls.NAME is None:
                cls.NAME = cls.ID

            for required_key in ("ID", "NAME", "URL"):
                assert getattr(cls, required_key), f"Define {cls.__name__}.{required_key}"

            if not cls.SUB_URLS:
                cls.SUB_URLS = [("index", cls.URL)]

            if cls.ID in scraper_classes:
                raise AssertionError(f"Duplicate name '{cls.ID}' for class {cls.__name__}")

            scraper_classes[cls.ID] = cls

    def __init__(self, verbose: bool = False, caching: Union[bool, str] = False):
        self.verbose = verbose
        self.caching = caching
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "github.com/defgsus/frontpage-archive-2"
        }
        self.report = {
            "files": 0,
            "articles": 0,
            "scripts": 0,
            "exceptions": [],
        }
        self.status = {}

    @classmethod
    def path(cls) -> Path:
        return cls.BASE_PATH / cls.ID

    def iter_files(self) -> Generator[Tuple[str, str, requests.Response, str], None, None]:
        """
        Yield tuples of (url, short-filename, text-content)

        The base method yields all urls, filenames and web responses from self.SUB_URLS
        """
        first_page = None
        for filename, url in self.SUB_URLS:

            try:
                response = self.request(url)
                content = response.text

                if first_page is None:
                    first_page = {"url": url, "content": content}

                yield url, filename, response, content
            except:
                self.log(traceback.format_exc())
                pass

        if first_page is not None:
            yield from self.iter_sub_link_files(**first_page)

    def iter_sub_link_files(
            self, url: str, content: str
    ) -> Generator[Tuple[str, str, requests.Response, str], None, None]:
        """
        Iterates through self.SUB_LINK_NAMES and yields all response of links
        whose text matches one of the names.

        :param markup: str of html
        """
        requested_urls = set()
        filename_counter = dict()

        soup = self.to_soup(content)
        base_url = url
        for a in soup.find_all("a"):
            if not a.text:
                continue

            link_name = a.text.strip()
            if a.get("href") and link_name in self.SUB_LINK_NAMES:

                url = self.url_join(base_url, a["href"])
                if url in requested_urls:
                    continue
                requested_urls.add(url)

                filename = "".join(c for c in link_name.lower() if "a" <= c <= "z")
                filename_counter[filename] = filename_counter.get(filename, 0) + 1

                if filename_counter[filename] > 1:
                    filename = f"{filename}{filename_counter[filename]}"

                try:
                    response = self.request(url)
                except:
                    self.log(traceback.format_exc())
                    continue

                yield url, filename, response, response.text

    def download(self, store_files: bool = True):
        """
        Download all files via `iter_files`,
        scrape the articles via `iter_articles`
        and store to disk.

        `self.report` is filled with summary infos
        """
        try:
            timestamp = datetime.datetime.utcnow().replace(microsecond=0)
            for url, short_filename, response, content in self.iter_files():

                file_data = {
                    "timestamp": timestamp.isoformat(),
                    "url": url,
                    "response": {
                        "status": response.status_code,
                    },
                    "scripts": [],
                    "articles": [],
                }
                try:
                    for article in self.iter_articles(url, short_filename, content):
                        file_data["articles"].append(
                            self.finalize_article_dict(url, short_filename, article)
                        )
                        self.report["articles"] += 1
                except:
                    self.report["exceptions"].append({
                        {"in": "iter_articles", "message": traceback.format_exc(limit=-2)}
                    })

                try:
                    for script in self.iter_scripts(url, short_filename, content):
                        file_data["scripts"].append(script)
                        self.report["scripts"] += 1
                except:
                    self.report["exceptions"].append({
                        {"in": "iter_scripts", "message": traceback.format_exc(limit=-2)}
                    })

                filename = self.path() / f"{short_filename}.json"

                if store_files:
                    os.makedirs(str(filename.parent), exist_ok=True)
                    self.log("storing", filename)
                    filename.write_text(json.dumps(file_data, indent=2, ensure_ascii=False))
                self.report["files"] += 1

                timestamp = datetime.datetime.utcnow().replace(microsecond=0)
        except:
            self.report["exceptions"].append({
                {"in": "iter_files", "message": traceback.format_exc(limit=-2)}
            })

    def log(self, *args):
        if self.verbose:
            print(f"{self.__class__.__name__}:", *args, file=sys.stderr)

    def request(
            self,
            url: str,
            method: str = "GET",
            **kwargs,
    ) -> requests.Response:
        """
        Do a HTTP request

        :param url: str, full url
        :param method: str, defaults to "GET"
        :param kwargs: any additional requests.request() arguments
        :return: requests.Response instance
        """
        cache_filename = self.CACHE_PATH / self.ID / hashlib.md5(f"{method} {url} {kwargs}".encode("utf-8")).hexdigest()

        if self.caching in (True, "read"):
            if cache_filename.exists():
                return pickle.loads(cache_filename.read_bytes())

        kwargs.setdefault("timeout", self.REQUEST_TIMEOUT)
        self.log("requesting", url)

        try:
            if self.USE_SESSION:
                response = self.session.request(method=method, url=url, **kwargs)
            else:
                response = requests.request(method=method, url=url, **kwargs)
            self.log(response.status_code, f"{len(response.content):,}")

            if self.caching in (True, "write"):
                os.makedirs(str(cache_filename.parent), exist_ok=True)
                cache_filename.write_bytes(pickle.dumps(response))

            return response
        except Exception as e:
            self.report["exceptions"].append({
                "in": "request",
                "url": url,
                "message": f"{e.__class__.__name__}: {e}",
            })
            raise

    @classmethod
    def url_join(cls, base: str, url: str) -> str:
        return urllib.parse.urljoin(base, url)

    @classmethod
    def to_soup(cls, html: str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(html, features="html.parser")

    @classmethod
    def strip(cls, x: Optional[Union[str, bs4.Tag]]) -> Optional[str]:
        if x is None:
            return None
        elif isinstance(x, str):
            text = x
        elif isinstance(x, bs4.Tag):
            text = x.text
        else:
            raise TypeError(f"Can not strip type {type(x).__name__} ({x})")

        if text is None:
            return None

        text = text.strip().replace("\n", " ").replace("\t", " ")
        return _RE_MULTI_SPACE.sub(" ", text)

    @classmethod
    def create_article_dict(
            cls,
            title: Optional[str] = None,
            teaser: Optional[str] = None,
            url: Optional[str] = None,
            image_url: Optional[str] = None,
            image_title: Optional[str] = None,
            author: Optional[str] = None,
            topic: Optional[str] = None,
    ) -> dict:
        return {
            key: value
            for key, value in {
                "title": title,
                "topic": topic,
                "teaser": teaser,
                "url": url,
                "author": author,
                "image_url": image_url,
                "image_title": image_title,
            }.items()
            if value
        }

    def finalize_article_dict(self, url: str, filename: str, article: dict) -> dict:
        article = {
            key: value
            for key, value in article.items()
            if value
        }
        if article.get("image_url"):
            if article["image_url"].startswith("data:"):
                del article["image_url"]

        for key in ("url", "image_url"):
            article_url = article.get(key)
            if article_url:
                if article_url.startswith("/"):
                    article[key] = self.url_join(url, article_url)

        return article

    def find_headline(self, tag: bs4.Tag) -> Optional[bs4.Tag]:
        return tag.find("h3") or tag.find("h2") or tag.find("h1") or tag.find("header")

    def iter_articles(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        """
        Override this to extract article data from each scraped file.

        Base implementation looks for common <article> tag structures
        """
        soup = self.to_soup(content)
        for tag in soup.find_all("article"):
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

    def patch_article(self, article: dict, tag: bs4.BeautifulSoup):
        pass

    def iter_scripts(self, url: str, filename: str, content: str) -> Generator[dict, None, None]:
        soup = self.to_soup(content)
        for tag in soup.find_all("script"):

            if not tag.get("src"):
                continue

            text = self.strip(tag.text)
            if not text:
                text = None
            else:
                text = text[:1000]

            yield {
                "type": tag.get("type"),
                "src": self.url_join(url, tag["src"]) if tag.get("src") else None,
                "id": tag.get("id"),
                "text": text,
            }


_RE_MULTI_SPACE = re.compile(r"\s+")
