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
