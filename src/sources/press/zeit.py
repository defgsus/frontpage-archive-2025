from ...scraper import Scraper


class Zeit(Scraper):
    ID = "zeit.de"
    URL = "https://www.zeit.de/"
    USE_SESSION = False
    SUB_URLS = [
        ("index", URL + "index"),

        ("politik", URL + "politik/index"),
        ("gesellschaft", URL + "gesellschaft/index"),
        ("wirtschaft", URL + "wirtschaft/index"),
        ("kultur", URL + "kultur/index"),
        ("wissen", URL + "wissen/index"),
        ("gesundheit", URL + "gesundheit/index"),
        ("digital", URL + "digital/index"),
        ("campus", URL + "campus/index"),
        ("sinn", URL + "sinn/index"),
        ("arbeit", URL + "arbeit/index"),
        ("sport", URL + "sport/index"),
        ("zeit-magazin", URL + "zeit-magazin/index"),
        ("news", URL + "news/index"),
        ("christ-und-welt", URL + "christ-und-welt"),
    ]


class ZeitSchule(Scraper):
    ID = "zeitfuerdieschule.de"
    URL = "https://www.zeitfuerdieschule.de"
    SUB_URLS = [
        ("index", URL),
        ("werte", URL + "/themen/werte/"),
        ("demokratie", URL + "/themen/demokratie/"),
        ("deutschland", URL + "/themen/deutschland/"),
    ]
