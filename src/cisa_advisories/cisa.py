from httpx import AsyncClient
from loguru import logger
from asyncio import Semaphore


class CISA:
    def __init__(self):
        self.client = AsyncClient(timeout=120.0)
        # Allow some concurrent requests, but stay conservative
        self.concurrency_limit = Semaphore(5)

    async def scrape_index(self, page: int):
        # Sort by last revised, in order to update our knowledge base if an advisory has
        # been updated
        params = {"sort_by": "field_last_updated", "url": "", "page": page}
        url = "https://www.cisa.gov/news-events/cybersecurity-advisories"
        async with self.concurrency_limit:
            logger.info(f"Scraping index page {page}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()

        return response.text

    async def scrape_advisory(self, link: str) -> str:
        url = f"https://www.cisa.gov{link}"
        async with self.concurrency_limit:
            logger.info(f"Scraping advisory {link}")
            response = await self.client.get(url)
            response.raise_for_status()

        return response.text
