from ...scraper import Scraper


class TOnline(Scraper):
    ID = "t-online.de"
    URL = "https://www.t-online.de/"
    SUB_URLS = [
        ("index", URL),
        ("politik", URL + "nachrichten/"),
        ("panorama", URL + "nachrichten/panorama/"),
        ("sport", URL + "sport/"),
        ("unterhaltung", URL + "unterhaltung/"),
    ]
    SUB_LINK_NAMES = [
        "Coronavirus",
    ]