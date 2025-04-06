import json
import os
from os.path import join
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CISA Advisories")

ADVISORY_DIR = os.environ.get("ADVISORY_DIR")
if not ADVISORY_DIR:
    raise ValueError("ADVISORY_DIR environment variable is not set")

with open(join(ADVISORY_DIR, "index.json"), "r") as f:
    index = json.load(f)

@mcp.tool()
def search_cisa_advisories(query: str) -> list[str]:
    """
    Search for CISA advisories. 
    
    Returns:
        A list of markdown documents, each representing an advisory.
    """
    matching_advisory_links = [advisory["link"] for advisory in index.values() if query.lower() in advisory["title"].lower()]

    advisories = []
    for advisory in matching_advisory_links:
        filename = advisory.split("/")[-1]
        with open(join(ADVISORY_DIR, "markdown", f"{filename}.md"), "r") as f:
            advisories.append(f.read())

    return advisories
