import asyncio
import json
from os import makedirs
from os.path import exists, join

import click
from .parser import advisory_to_markdown, get_advisories, get_last_page

from .cisa import CISA
from loguru import logger


def load_checkpoint(output_dir: str) -> str:
    if exists(join(output_dir, "checkpoint.txt")):
        with open(join(output_dir, "checkpoint.txt"), "r") as f:
            return f.read()
    else:
        return ""


def save_checkpoint(link: str, output_dir: str):
    with open(join(output_dir, "checkpoint.txt"), "w") as f:
        f.write(link)


async def get_and_process_advisory(link: str, cisa_client: CISA):
    """
    Download an advisory, convert it to markdown, and save both HTML and markdown to
    disk.
    """
    advisory_html = await cisa_client.scrape_advisory(link)

    filename = link.split("/")[-1]

    with open(join("advisories", "html", f"{filename}.html"), "w") as f:
        f.write(advisory_html)

    advisory_markdown = advisory_to_markdown(advisory_html)

    with open(join("advisories", "markdown", f"{filename}.md"), "w") as f:
        f.write(advisory_markdown)


async def download(max_pages: int, output_dir: str):
    cisa_client = CISA()

    # Initialize the output directories
    if not exists(output_dir):
        makedirs(output_dir)

    if not exists(join(output_dir, "html")):
        makedirs(join(output_dir, "html"))

    if not exists(join(output_dir, "markdown")):
        makedirs(join(output_dir, "markdown"))

    checkpoint = load_checkpoint(output_dir)

    if checkpoint:
        logger.info(f"Resuming from checkpoint: {checkpoint}")
    else:
        logger.info("Starting from the beginning")

    # Iterate over index pages, collecting advisories until we hit the checkpoint
    current_page = 0
    last_page = max_pages
    advisories = []
    while True:
        index_html = await cisa_client.scrape_index(page=current_page)

        # We won't know how long to loop for until the first page has been scraped
        if last_page == 0:
            last_page = get_last_page(index_html)

        for i, advisory in enumerate(get_advisories(index_html)):
            # We've hit the checkpoint. Time to stop
            if advisory["link"] == checkpoint:
                logger.info(f"Reached checkpoint: {checkpoint}")
                last_page = current_page
                break

            advisories.append(advisory)

        if current_page == last_page:
            break

        current_page += 1

    logger.info(f"Found {len(advisories)} advisories to process")

    # Finally, download each advisory and convert it to markdown
    tasks = [
        get_and_process_advisory(link=advisory["link"], cisa_client=cisa_client)
        for advisory in advisories
    ]
    await asyncio.gather(*tasks)

    # Update the checkpoint to the first advisory (the most recently-revised one)
    if advisories:
        save_checkpoint(advisories[0]["link"], output_dir)

    # Save an index of advisories, for use with the MCP server
    if exists(join(output_dir, "index.json")):
        with open(join(output_dir, "index.json"), "r") as f:
            index = json.load(f)
    else:
        index = {}

    for advisory in advisories:
        index[advisory["link"]] = advisory


@click.command()
@click.option(
    "--max-pages",
    type=int,
    default=25,
    help="The number of pages to scrape at most. Set to 0 to scrape all pages.",
)
@click.option(
    "--output-dir",
    type=str,
    default="advisories",
    help="The directory to save the advisories to.",
)
def cli(max_pages: int, output_dir: str):
    asyncio.run(download(max_pages, output_dir))


if __name__ == "__main__":
    cli()
