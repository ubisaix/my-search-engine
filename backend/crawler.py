import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from backend.database import add_document


USER_AGENT = "MySearchEngineBot/1.0"


def crawl(url):

    try:

        headers = {
            "User-Agent": USER_AGENT
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            ""
        )

        if "text/html" not in content_type:
            print("Not HTML:", url)
            return

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # არასაჭირო ელემენტების წაშლა
        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        # გვერდის სათაური
        title = ""

        if soup.title:
            title = soup.title.get_text(
                " ",
                strip=True
            )

        if not title:
            title = url

        # გვერდის ტექსტი
        text = soup.get_text(
            " ",
            strip=True
        )

        # ზედმეტი სივრცეების მოცილება
        text = " ".join(
            text.split()
        )

        if not text:
            print("No text:", url)
            return

        # PostgreSQL-ში შენახვა
        add_document(
            title,
            url,
            text
        )

        print(
            f"Indexed: {title} -> {url}"
        )

        # გვერდზე არსებული ბმულები
        links = set()

        for link in soup.find_all(
            "a",
            href=True
        ):

            absolute_url = urljoin(
                url,
                link["href"]
            )

            parsed = urlparse(
                absolute_url
            )

            if parsed.scheme in (
                "http",
                "https"
            ):
                links.add(
                    absolute_url
                )

        print(
            f"Found {len(links)} links"
        )

        return list(links)

    except Exception as error:

        print(
            f"Error crawling {url}: {error}"
        )

        return []


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage: python backend/crawler.py URL"
        )

        sys.exit(1)

    url = sys.argv[1]

    crawl(url)
