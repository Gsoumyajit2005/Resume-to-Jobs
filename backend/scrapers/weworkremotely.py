"""
WeWorkRemotely Scraper Module.

Scrapes job listings from weworkremotely.com.
"""
import asyncio
import random
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from scrapers.common import ScraperBase
from config import settings


class WeWorkRemotelyScraper(ScraperBase):
    """Scraper for WeWorkRemotely job listings."""

    NAME = "weworkremotely"
    BASE_URL = "https://weworkremotely.com"
    JOBS_URL = f"{BASE_URL}/remote-jobs"

    def __init__(self):
        """Initialize the WeWorkRemotely scraper."""
        super().__init__()

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on WeWorkRemotely.

        Args:
            query: Search query (skills/roles)
            location: Optional location filter (ignored)
            max_results: Maximum results to return

        Returns:
            List of raw job data dictionaries
        """
        jobs = []
        seen_ids = set()

        # Build query URL
        url = self.JOBS_URL
        params = {}

        print(f"[WeWorkRemotely] Fetching from {url}")

        html = await self._get_page(url, params)

        if not html:
            return jobs

        soup = self._parse_html(html)

        # Find job listings - WeWorkRemotely uses specific structure
        job_listings = soup.find_all("li", class_=re.compile(r"feature|normal", re.I))

        for idx, item in enumerate(job_listings):
            try:
                if len(jobs) >= max_results:
                    break
                job = self._extract_job(item)
                if job and job["id"] not in seen_ids:
                    jobs.append(job)
                    seen_ids.add(job["id"])
            except Exception:
                # Skip parsing errors
                continue

        return jobs

    def _extract_job(self, item) -> Optional[Dict[str, Any]]:
        """Extract job data from a job listing element."""
        # Get job ID from href or generate one
        link_el = item.find("a", href=re.compile(r"/remote-jobs/", re.I))
        if link_el:
            href = link_el["href"]
            # Extract slug from URL: /remote-jobs/slug
            match = re.search(r"/remote-jobs/([^/?]+)", href)
            job_id = match.group(1) if match else f"wwr_{hash(str(item)[:100]) % 100000}"
        else:
            job_id = f"wwr_{hash(str(item)[:100]) % 100000}"

        # Get job title - look for h3 element specifically
        title_el = item.find("h3")
        title = title_el.get_text(strip=True) if title_el else "Unknown"

        # Get company name - the company name appears as text right after the h3 title
        # or as an <a> link with href /company/
        company = "Anonymous"
        # First, look for company link
        company_link = item.find("a", href=re.compile(r"/company/", re.I))
        if company_link:
            # Extract company name from URL path like /company/prepterminal-com
            href = company_link.get("href", "")
            match = re.search(r'/company/([^/]+)', href)
            if match:
                company_slug = match.group(1)
                # Convert slug to readable name: prepterminal-com -> Prepterminal
                company = company_slug.replace('-', ' ').title()
                if company == "View Company Profile":
                    company = "Anonymous"
            else:
                company = company_link.get_text(strip=True)
        else:
            # Try to extract from sibling text after h3
            if title_el and title_el.next_sibling:
                # Get text nodes after title
                next_text = ""
                for sibling in title_el.next_siblings:
                    if isinstance(sibling, str):
                        next_text += sibling.strip()
                    elif sibling.name == "img":
                        # Skip image tags
                        continue
                    elif sibling.name in ["span", "div"]:
                        # Get text from these elements
                        next_text += sibling.get_text(strip=True)
                    else:
                        break
                # The company name is usually the first meaningful text after title
                # Remove tags like "New", "Featured", etc.
                next_text = next_text.strip()
                if next_text:
                    company = next_text.split()[0] if next_text else "Anonymous"
                    # Clean up: remove trailing punctuation, emojis, etc.
                    company = company.strip()
                    # Remove trailing tags and emojis
                    company = re.sub(r'\s+.*$', '', company)
                    company = company[:50]
                    if not company:
                        company = "Anonymous"

        # Get location - look for location text after company
        location = "Remote"
        # If there's a location span/div, use it
        location_el = item.find(["span", "div"], string=re.compile(r'(USA|United States|Anywhere|Worldwide|Remote|Tel Aviv|Israel|Canada|Europe)', re.I))
        if location_el:
            location = location_el.get_text(strip=True)

        # Get description snippet from data attributes or next element
        description = ""
        # Don't include the jumbled text from the page

        # Get apply URL
        apply_url = None
        if link_el:
            href = link_el["href"]
            if href.startswith("/"):
                apply_url = f"{self.BASE_URL}{href}"

        # Get posted date
        posted_date = None
        date_el = item.find(["span", "div"], class_=re.compile(r"date|time|new", re.I))
        if date_el:
            posted_date = self._parse_date(date_el.get_text(strip=True))

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

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from text."""
        date_text = date_text.lower().strip()

        now = datetime.utcnow()

        if "today" in date_text or "just" in date_text or "new" in date_text:
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


async def test_weworkremotely_scraper():
    """Test the WeWorkRemotely scraper."""
    async with WeWorkRemotelyScraper() as scraper:
        print(f"Testing WeWorkRemotely scraper")

        jobs = await scraper.search_jobs(
            query="Python developer",
            max_results=10
        )

        print(f"Found {len(jobs)} jobs")

        for job in jobs[:3]:
            print(f"  - {job['title']} at {job['company']} ({job['location']})")


if __name__ == "__main__":
    asyncio.run(test_weworkremotely_scraper())
