"""
LinkedIn Scraper Module.

Scrapes job listings from LinkedIn.
Includes anti-blocking measures and retry logic.
"""
import asyncio
import random
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from scrapers.common import ScraperBase, ScraperError
from config import settings


class LinkedInScraper(ScraperBase):
    """Scraper for LinkedIn job listings."""

    NAME = "linkedin"
    BASE_URL = "https://www.linkedin.com"

    def __init__(self):
        """Initialize the LinkedIn scraper."""
        super().__init__()
        self._search_url = f"{self.BASE_URL}/jobs/search"
        # LinkedIn requires specific headers
        self._custom_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0",
        }

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on LinkedIn.

        Args:
            query: Search query (skills/roles)
            location: Optional location filter
            max_results: Maximum results to return

        Returns:
            List of raw job data dictionaries
        """
        jobs = []
        seen_ids = set()

        # LinkedIn search parameters
        params = {
            "keywords": query,
            "f_WT": 2,  # Remote jobs
            "f_E": [1, 2, 3, 4, 5],  # Experience levels
        }

        if location:
            params["location"] = location

        # LinkedIn returns 25 jobs per page
        num_pages = (max_results // 25) + 1

        for page in range(num_pages):
            params["start"] = page * 25

            html = await self._get_page_with_custom_headers(
                self._search_url,
                params
            )

            if not html:
                break

            parsed_jobs = self._parse_jobs_html(html, seen_ids)
            jobs.extend(parsed_jobs)
            seen_ids.update(job["id"] for job in parsed_jobs)

            if len(jobs) >= max_results:
                break

            # LinkedIn requires longer delays
            await asyncio.sleep(random.uniform(2.0, 4.0))

        return jobs[:max_results]

    async def _get_page_with_custom_headers(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get page with custom headers for LinkedIn.

        Args:
            url: URL to fetch
            params: Query parameters

        Returns:
            HTML content
        """
        for attempt in range(settings.RETRY_COUNT):
            try:
                await self.rate_limiter.acquire()

                if not self._client:
                    await self._create_client()

                # Override headers for this request
                headers = self._custom_headers.copy()
                headers.update(settings.get_headers())

                response = await self._client.get(
                    url,
                    params=params,
                    headers=headers
                )

                if response.status_code == 200:
                    return response.text

                elif response.status_code == 403:
                    # LinkedIn blocked us, wait and retry
                    await asyncio.sleep(3 ** attempt * random.uniform(1, 3))

                elif response.status_code >= 500:
                    await asyncio.sleep(2 ** attempt * random.uniform(0.5, 2))

                else:
                    raise ScraperError(
                        f"LinkedIn HTTP {response.status_code}"
                    )

            except asyncio.TimeoutError:
                if attempt == settings.RETRY_COUNT - 1:
                    raise
                await asyncio.sleep(2 ** attempt * random.uniform(0.5, 2))

        return None

    def _parse_jobs_html(
        self,
        html: str,
        seen_ids: set
    ) -> List[Dict[str, Any]]:
        """Parse job listings from LinkedIn HTML."""
        soup = self._parse_html(html)
        jobs = []

        # LinkedIn uses various job card classes
        job_cards = soup.find_all(["div", "li"], class_=re.compile(
            r"job-search-card|result-card|jobs-posting", re.I
        ))

        for card in job_cards:
            try:
                job = self._extract_job(card)
                if job and job["id"] not in seen_ids:
                    jobs.append(job)
            except Exception:
                continue

        return jobs

    def _extract_job(self, card) -> Optional[Dict[str, Any]]:
        """Extract job data from a LinkedIn job card."""
        # Get job ID from data ID or URL
        job_id = self._get_attr(card, "data-entity-urn", "data-job-id", "id")
        if not job_id:
            # Generate from card content
            job_id = f"link_{hash(str(card)[:200]) % 100000}"

        # Get job title
        title_el = card.find(["h3", "h2", "span"], class_=re.compile(
            r"job-title|base-title", re.I
        ))
        title = title_el.get_text(strip=True) if title_el else "Unknown Role"

        # Get company name
        company_el = card.find(["h4", "span"], class_=re.compile(
            r"company-name|company-url", re.I
        ))
        company = company_el.get_text(strip=True) if company_el else "Anonymous"

        # Get location
        location_el = card.find(["span"], class_=re.compile(
            r"job-location|location", re.I
        ))
        location = location_el.get_text(strip=True) if location_el else ""

        # Get description snippet
        desc_el = card.find(["p", "div"], class_=re.compile(
            r"description|summary", re.I
        ))
        description = desc_el.get_text(strip=True)[:500] if desc_el else ""

        # Get posted date
        date_el = card.find(["span"], class_=re.compile(
            r"job-post-date|relative-time", re.I
        ))
        posted_date = self._parse_date(date_el.get_text(strip=True)) if date_el else None

        # Get apply URL from link
        apply_url = None
        link_el = card.find("a", href=True)
        if link_el:
            href = link_el["href"]
            if href.startswith("/"):
                apply_url = f"{self.BASE_URL}{href}"
            elif href.startswith("http"):
                apply_url = href

        return {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "apply_url": apply_url,
            "source": self.NAME,
            "is_active": True,
            "posted_date": posted_date,
            "scraped_at": datetime.utcnow(),
        }

    def _get_attr(self, element, *attrs) -> Optional[str]:
        """Get first available attribute value."""
        for attr in attrs:
            if attr in element.attrs:
                value = element[attr]
                if value:
                    return str(value)
        return None

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from LinkedIn format."""
        date_text = date_text.lower().strip()

        now = datetime.utcnow()

        if "today" in date_text or "just posted" in date_text:
            return now

        if "hour" in date_text:
            match = re.search(r"(\d+)\s*hours? ago", date_text)
            if match:
                return now - timedelta(hours=int(match.group(1)))

        if "day" in date_text:
            match = re.search(r"(\d+)\s*days? ago", date_text)
            if match:
                return now - timedelta(days=int(match.group(1)))

        if "week" in date_text:
            match = re.search(r"(\d+)\s*weeks? ago", date_text)
            if match:
                return now - timedelta(weeks=int(match.group(1)))

        if "month" in date_text:
            match = re.search(r"(\d+)\s*months? ago", date_text)
            if match:
                return now - timedelta(days=int(match.group(1)) * 30)

        return None


async def test_linkedin_scraper():
    """Test the LinkedIn scraper."""
    async with LinkedInScraper() as scraper:
        print(f"Testing LinkedIn scraper")

        jobs = await scraper.search_jobs(
            query="Python engineer",
            location="United States",
            max_results=10
        )

        print(f"Found {len(jobs)} jobs")

        for job in jobs[:3]:
            print(f"  - {job['title']} at {job['company']} ({job['location']})")


if __name__ == "__main__":
    asyncio.run(test_linkedin_scraper())
