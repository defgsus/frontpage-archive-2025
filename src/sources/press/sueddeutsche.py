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
