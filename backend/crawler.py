import sys
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from backend.database import add_document


USER_AGENT = "MySearchEngineBot/1.0"

MAX_PAGES = 10

visited = set()


def crawl_page(url):

    if url in visited:
        return []

    visited.add(url)

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

        if "text/html" not in response.headers.get(
            "content-type",
            ""
        ):
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        title = ""

        if soup.title:
            title = soup.title.get_text(
                " ",
                strip=True
            )

        if not title:
            title = url

        text = soup.get_text(
            " ",
            strip=True
        )

        text = " ".join(
            text.split()
        )

        if text:

            add_document(
                title,
                url,
                text
            )

            print(
                f"Indexed: {title}"
            )

        links = set()

        base_domain = urlparse(url).netloc

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

            if parsed.scheme not in (
                "http",
                "https"
            ):
                continue

            if parsed.netloc != base_domain:
                continue

            clean_url = (
                parsed.scheme
                + "://"
                + parsed.netloc
                + parsed.path
            )

            if clean_url not in visited:

                links.add(clean_url)

        return list(links)

    except Exception as error:

        print(
            f"Error: {url} -> {error}"
        )

        return []


def crawl(start_url):

    queue = [start_url]

    while queue and len(visited) < MAX_PAGES:

        url = queue.pop(0)

        print(
            f"Crawling: {url}"
        )

        new_links = crawl_page(url)

        for link in new_links:

            if (
                link not in visited
                and link not in queue
                and len(visited) + len(queue) < MAX_PAGES
            ):

                queue.append(link)

        time.sleep(1)

    return list(visited)


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage: python backend/crawler.py URL"
        )

        sys.exit(1)

    crawl(
        sys.argv[1]
    )
