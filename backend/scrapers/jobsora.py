"""
Jobsora Scraper Module.

Jobsora is a job board with minimal bot protection.
"""
import asyncio
import random
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from scrapers.common import ScraperBase, ScraperError
from config import settings


class JobsoraScraper(ScraperBase):
    """Scraper for Jobsora job listings."""

    NAME = "jobsora"
    BASE_URL = "https://www.jobsora.com"

    def __init__(self):
        """Initialize the Jobsora scraper."""
        super().__init__()
        self._search_url = f"{self.BASE_URL}/jobsearch"

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on Jobsora.

        Args:
            query: Search query (skills/roles)
            location: Optional location filter
            max_results: Maximum results to return

        Returns:
            List of raw job data dictionaries
        """
        jobs = []
        seen_ids = set()

        # Build query parameters
        params = {
            "q": query,
        }

        if location:
            params["l"] = location

        # Jobsora returns 10 jobs per page
        num_pages = (max_results // 10) + 1

        for page in range(num_pages):
            params["page"] = page + 1

            url = self._search_url
            print(f"[Jobsora] Fetching page {page+1}: {url}")
            html = await self._get_page(url, params)

            if not html:
                print(f"[Jobsora] No HTML returned for page {page+1}")
                break

            parsed_jobs = self._parse_jobs_html(html, seen_ids, max_results)
            jobs.extend(parsed_jobs)
            seen_ids.update(job["id"] for job in parsed_jobs)

            if len(jobs) >= max_results:
                break

            await asyncio.sleep(random.uniform(1.0, 2.0))

        print(f"[Jobsora] Returning {len(jobs)} jobs")
        return jobs

    def _parse_jobs_html(
        self,
        html: str,
        seen_ids: set,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Parse job listings from HTML."""
        soup = self._parse_html(html)
        jobs = []

        # Jobsora uses specific classes for job cards
        job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job-card|job-item|job__item", re.I))

        print(f"[Jobsora] Found {len(job_cards)} job cards")

        for card in job_cards:
            try:
                if len(jobs) >= max_results:
                    break
                job = self._extract_job(card)
                if job and job["id"] not in seen_ids:
                    jobs.append(job)
            except Exception as e:
                print(f"[Jobsora] Error extracting job: {e}")
                continue

        return jobs

    def _extract_job(self, card) -> Optional[Dict[str, Any]]:
        """Extract job data from a job card element."""
        # Get job ID
        job_id = self._get_attr(card, "data-id", "data-job-id", "id")
        if not job_id:
            job_id = f"js_{hash(str(card)[:100]) % 100000}"

        # Get job title
        title_el = card.find(["a", "h2", "h3", "span"], class_=re.compile(r"job-title|title|job__title", re.I))
        title = title_el.get_text(strip=True) if title_el else "Unknown Role"

        # Get company name
        company_el = card.find(["span", "div"], class_=re.compile(r"company|employer|job__company", re.I))
        company = company_el.get_text(strip=True) if company_el else "Anonymous"

        # Get location
        location_el = card.find(["span", "div"], class_=re.compile(r"location|address|job__location", re.I))
        location = location_el.get_text(strip=True) if location_el else ""

        # Get description snippet
        desc_el = card.find(["p", "div"], class_=re.compile(r"description|summary|job__description", re.I))
        description = desc_el.get_text(" ", strip=True)[:500] if desc_el else ""

        # Get apply URL
        apply_url = None
        link_el = card.find("a", href=True)
        if link_el:
            href = link_el["href"]
            if href.startswith("/"):
                apply_url = f"{self.BASE_URL}{href}"
            elif href.startswith("http"):
                apply_url = href

        # Get posted date
        date_el = card.find(["span", "div"], class_=re.compile(r"date|ago|time", re.I))
        posted_date = self._parse_date(date_el.get_text(strip=True)) if date_el else None

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
        """Parse date from text."""
        date_text = date_text.lower().strip()

        now = datetime.utcnow()

        if "today" in date_text or "just posted" in date_text:
            return now

        if "hour" in date_text:
            match = re.search(r"(\d+)\s*hours?", date_text)
            if match:
                return now - timedelta(hours=int(match.group(1)))

        if "day" in date_text:
            match = re.search(r"(\d+)\s*days?", date_text)
            if match:
                return now - timedelta(days=int(match.group(1)))

        if "week" in date_text:
            match = re.search(r"(\d+)\s*weeks?", date_text)
            if match:
                return now - timedelta(weeks=int(match.group(1)))

        return None


async def test_jobsora_scraper():
    """Test the Jobsora scraper."""
    async with JobsoraScraper() as scraper:
        print(f"Testing Jobsora scraper")

        jobs = await scraper.search_jobs(
            query="Python developer",
            max_results=10
        )

        print(f"Found {len(jobs)} jobs")

        for job in jobs[:3]:
            print(f"  - {job['title']} at {job['company']} ({job['location']})")


if __name__ == "__main__":
    asyncio.run(test_jobsora_scraper())
