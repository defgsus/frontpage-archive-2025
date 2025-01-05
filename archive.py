import argparse
import datetime
import traceback
import json
from multiprocessing.pool import ThreadPool
from typing import List

import tabulate

import src.sources  # register scraper classes
from src.scraper import Scraper, scraper_classes
from src.summary import summary, PROJECT_PATH


def parse_args() -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "command", type=str,
        choices=["list", "scrape", "readme", "dump"],
        help="What to do?"
    )
    parser.add_argument(
        "-f", "--filter", type=str, nargs="*",
        help="One or more scraper names to limit the download"
    )
    parser.add_argument(
        "-v", "--verbose", type=bool, nargs="?", default=False, const=True,
        help="Print a lot of stuff"
    )
    parser.add_argument(
        "-c", "--cache", type=bool, nargs="?", default=False, const=True,
        help="Cache requests (write and read next time)"
    )
    parser.add_argument(
        "-j", "--threads", type=int, default=1,
        help="Number of parallel threads (per scraper)"
    )

    return vars(parser.parse_args())


def scrape(scraper: Scraper) -> str:
    """
    Run the scraper, return result message text
    """
    msg = f"### {scraper.ID}\n\n"

    try:
        scraper.download()

        for key, value in scraper.report.items():
            if value:
                if isinstance(value, list):
                    msg += f"- {len(value)} {key}"
                else:
                    msg += f"- {value} {key}\n"

    except:
        msg += f"```\n{traceback.format_exc(limit=-2)}```\n"

    return msg


def dump_articles(scrapers: List[Scraper]):
    for scraper in scrapers:
        print(f"\n-------- {scraper.ID} --------\n")
        for url, filename, response, content in scraper.iter_files():
            print(f"\n-- {scraper.ID} - {filename} --\n")
            for article in scraper.iter_articles(
                    scraper.URL, filename, content
            ):
                print(json.dumps(article, indent=2, ensure_ascii=False))


def main(
        command: str,
        filter: List[str],
        verbose: bool,
        cache: bool,
        threads: int,
):

    filtered_classes = []
    for name in sorted(scraper_classes.keys()):
        if not filter or name in filter:
            filtered_classes.append(scraper_classes[name])

    scrapers = [
        scraper_class(verbose=verbose, caching=cache)
        for scraper_class in filtered_classes
    ]
    if command == "list":
        rows = []
        for scraper in scrapers:
            rows.append({
                "id": scraper.ID,
                "url": scraper.URL,
            })
        print(tabulate.tabulate(rows, tablefmt="pipe"))

    elif command == "scrape":
        print(f"update @ {datetime.datetime.utcnow().replace(microsecond=0)} UTC\n")

        messages = ThreadPool(threads).map(scrape, scrapers)
        messages.sort()

        print("\n".join(messages))

    elif command == "readme":
        readme_template = (PROJECT_PATH / "templates" / "README.md").read_text()
        readme_template %= {
            "table": summary(list(scraper_classes.values()))
        }
        (PROJECT_PATH / "README.md").write_text(readme_template)

    elif command == "dump":
        dump_articles(scrapers)


if __name__ == "__main__":
    main(**parse_args())
