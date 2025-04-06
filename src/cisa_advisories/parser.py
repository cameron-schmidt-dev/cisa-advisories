from typing import Generator
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

# I suspect the ATX heading style is more LLM-friendly than the default
converter = MarkdownConverter(heading_style="ATX")


def get_last_page(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    last = soup.find("a", class_="c-pager__link--last").get("href").split("page=")[-1]
    return int(last)


def get_advisories(html: str) -> Generator[dict, None, None]:
    """
    Parse a single page of the index and return advisory title, date, and links.
    """
    soup = BeautifulSoup(html, "html.parser")

    for advisory in soup.find_all("article"):
        date = advisory.find("time").text.strip()
        category = advisory.find("div", class_="c-teaser__meta").text.strip()
        title_h3 = advisory.find("h3", class_="c-teaser__title")
        title = title_h3.text.strip()
        link = title_h3.a["href"]

        yield {"date": date, "category": category, "title": title, "link": link}


def advisory_to_markdown(html: str) -> str:
    """
    Parse a single advisory page and return the advisory data.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Pull out just the body
    body = soup.find("main", class_="c-main")

    # Remove the footer
    for footer in body.find_all("div", class_="l-full__footer"):
        footer.decompose()

    # Convert to markdown
    markdown = converter.convert_soup(body)

    return markdown
