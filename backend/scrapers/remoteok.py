"""
RemoteOK Scraper Module.

Scrapes job listings from RemoteOK.com - uses their JSON API for reliability.
"""
import asyncio
import random
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from scrapers.common import ScraperBase, ScraperError, RateLimiter
from config import settings


class RemoteOKScraper(ScraperBase):
    """Scraper for RemoteOK job listings."""

    NAME = "remoteok"
    BASE_URL = "https://remoteok.com"
    API_URL = "https://remoteok.com/api"

    def __init__(self):
        """Initialize the RemoteOK scraper."""
        super().__init__()

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on RemoteOK using their JSON API.

        RemoteOK provides a simple JSON API endpoint.
        """
        jobs = []

        # RemoteOK's simple API endpoint for jobs
        # The API returns jobs as JSON
        url = f"{self.API_URL}/"

        # Parse query for tags (comma-separated)
        tags = query.replace(" ", ",").replace("+", ",")

        params = {
            "tags": tags,
        }

        try:
            # Direct HTTP request without going through the scraper client
            async with httpx.AsyncClient() as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                }
                response = await client.get(url, params=params, headers=headers, timeout=30)

                if response.status_code != 200:
                    return jobs

                # RemoteOK API returns an array with first element being metadata
                data = response.json()

                if isinstance(data, list) and len(data) > 1:
                    # Skip first element (metadata)
                    job_list = data[1:]

                    for item in job_list[:max_results]:
                        try:
                            job = self._parse_job_item(item)
                            if job:
                                jobs.append(job)
                        except Exception as e:
                            print(f"[RemoteOK] Error parsing job item: {e}")
                            continue

        except Exception as e:
            return jobs

        return jobs

    def _parse_job_item(self, item: dict) -> Optional[Dict[str, Any]]:
        """Parse a RemoteOK job item from API response."""
        try:
            # RemoteOK API format:
            # - id: position ID
            # - date: ISO timestamp
            # - logo: company logo URL
            # - company: company name
            # - position: job title
            # - location: location
            # - salary: salary info
            # - tags: comma-separated tags
            # - description: job description
            # - url: apply URL

            job_id = str(item.get("id", ""))
            if not job_id:
                return None

            # Extract skills from tags
            tags = item.get("tags", "")
            tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

            return {
                "id": job_id,
                "title": item.get("position", "Unknown"),
                "company": item.get("company", "Anonymous"),
                "location": item.get("location", "Remote"),
                "description": item.get("description", "")[:1000],
                "apply_url": f"https://remoteok.com/remote-jobs/{job_id}",
                "source": self.NAME,
                "is_active": True,
                "posted_date": self._parse_date(item.get("date")),
                "salary_range": item.get("salary"),
                "tags": tags_list,
                "scraped_at": datetime.utcnow(),
            }
        except Exception as e:
            return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from RemoteOK format."""
        if not date_str:
            return None

        try:
            # RemoteOK API returns ISO format date
            from datetime import datetime
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None


async def test_remoteok_scraper():
    """Test the RemoteOK scraper."""
    async with RemoteOKScraper() as scraper:
        print(f"Testing RemoteOK scraper")

        jobs = await scraper.search_jobs(
            query="Python remote",
            max_results=10
        )

        print(f"Found {len(jobs)} jobs")

        for job in jobs[:3]:
            print(f"  - {job['title']} at {job['company']} ({job['location']})")


if __name__ == "__main__":
    asyncio.run(test_remoteok_scraper())
