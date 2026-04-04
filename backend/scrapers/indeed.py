"""
Indeed Scraper Module.

 Scrapes job listings from Indeed.com.
 Uses unofficial scraping with proper error handling.
"""
import asyncio
import random
import re
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from scrapers.common import ScraperBase, ScraperError, ScraperTimeoutError
from config import settings


class IndeedScraper(ScraperBase):
    """Scraper for Indeed job listings."""

    NAME = "indeed"
    BASE_URL = "https://www.indeed.com"

    # Indeed uses different regional domains
    DOMAINS = [
        "https://www.indeed.com",
        "https://www.indeed.co.uk",
        "https://www.indeed.ca",
        "https://www.indeed.com.au",
    ]

    def __init__(self):
        """Initialize the Indeed scraper."""
        super().__init__()
        self.base_url = random.choice(self.DOMAINS)

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on Indeed.

        Args:
            query: Search query (skills/roles)
            location: Optional location filter
            max_results: Maximum results to return

        Returns:
            List of raw job data dictionaries
        """
        jobs = []
        seen_ids = set()

        # Build search URL
        params = {
            "q": query,
            "limit": 50,  # Indeed returns 10-15 per page
        }

        if location:
            params["l"] = location

        # Indeed pagination - fetch multiple pages
        num_pages = (max_results // 15) + 1

        for page in range(num_pages):
            offset = page * 10
            params["start"] = offset

            url = f"{self.base_url}/jobs"
            html = await self._get_page(url, params)

            if not html:
                break

            parsed_jobs = self._parse_jobs_html(html, seen_ids)
            jobs.extend(parsed_jobs)
            seen_ids.update(job["id"] for job in parsed_jobs)

            if len(jobs) >= max_results:
                break

            # Indeed requires delay between requests
            await asyncio.sleep(random.uniform(1.5, 3.0))

        return jobs[:max_results]

    def _parse_jobs_html(
        self,
        html: str,
        seen_ids: set
    ) -> List[Dict[str, Any]]:
        """Parse job listings from HTML."""
        soup = self._parse_html(html)
        jobs = []

        # Indeed uses various containers - look for job cards
        job_cards = soup.find_all(["div", "li"], class_=re.compile(r"jobsearch-SerpJobCard|result|job", re.I))

        for card in job_cards:
            try:
                job = self._extract_job_from_card(card)
                if job and job["id"] not in seen_ids:
                    jobs.append(job)
            except Exception:
                # Skip parsing errors
                continue

        return jobs

    def _extract_job_from_card(
        self,
        card
    ) -> Optional[Dict[str, Any]]:
        """Extract job data from a job card element."""
        # Get job ID
        job_id = self._get_attr(card, "data-jk", "data-jobid", "data-tjobs", "id")
        if not job_id:
            return None

        # Get job title
        title_el = card.find(["a", "h2", "span"], class_=re.compile(r"jobtitle|title", re.I))
        title = title_el.get_text(strip=True) if title_el else "Unknown Role"

        # Get company name
        company_el = card.find(["span", "div"], class_=re.compile(r"company|employer", re.I))
        company = company_el.get_text(strip=True) if company_el else "Anonymous"

        # Get location
        location_el = card.find(["span", "div"], class_=re.compile(r"location|address", re.I))
        location = location_el.get_text(strip=True) if location_el else ""

        # Get summary/description
        summary_el = card.find(["div", "span"], class_=re.compile(r"summary|snippet", re.I))
        description = summary_el.get_text(strip=True)[:500] if summary_el else ""

        # Get posted date
        date_el = card.find(["span", "div"], class_=re.compile(r"date|poste", re.I))
        posted_date = self._parse_date(date_el.get_text(strip=True)) if date_el else None

        # Get apply URL
        apply_url = None
        link_el = card.find("a", href=True)
        if link_el:
            href = link_el["href"]
            if href.startswith("/"):
                apply_url = f"{self.base_url}{href}"
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
                    return value
        return None

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from text like 'Today', '30+ days ago', etc."""
        date_text = date_text.lower().strip()

        now = datetime.utcnow()

        if "today" in date_text or "just posted" in date_text:
            return now

        if "yesterday" in date_text:
            return now - timedelta(days=1)

        # Parse numeric days
        match = re.search(r"(\d+)\s*days? ago", date_text)
        if match:
            days = int(match.group(1))
            return now - timedelta(days=days)

        # Parse '30+ days ago' as 30 days
        if "30+" in date_text or "30 days" in date_text:
            return now - timedelta(days=30)

        return None

    async def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific job.

        Args:
            job_id: Indeed job ID

        Returns:
            Job details dictionary
        """
        url = f"{self.base_url}/viewjob?jk={job_id}"
        html = await self._get_page(url)

        if not html:
            return None

        soup = self._parse_html(html)

        # Extract full description
        desc_el = soup.find(["div", "span"], class_=re.compile(r"jobdescription|description", re.I))
        description = desc_el.get_text(" ", strip=True) if desc_el else ""

        # Extract salary if available
        salary_el = soup.find(["span", "div"], class_=re.compile(r"salary|pay", re.I))
        salary = salary_el.get_text(strip=True) if salary_el else None

        # Extract job type
        job_type_el = soup.find(["span", "div"], class_=re.compile(r"jobtype|type", re.I))
        job_type = job_type_el.get_text(strip=True) if job_type_el else None

        return {
            "description": description,
            "salary_range": salary,
            "job_type": job_type,
        }


async def test_indeed_scraper():
    """Test the Indeed scraper."""
    async with IndeedScraper() as scraper:
        print(f"Testing Indeed scraper: {scraper.base_url}")

        jobs = await scraper.search_jobs(
            query="Python developer",
            location="San Francisco",
            max_results=10
        )

        print(f"Found {len(jobs)} jobs")

        for job in jobs[:3]:
            print(f"  - {job['title']} at {job['company']}")


if __name__ == "__main__":
    asyncio.run(test_indeed_scraper())
