"""
JobSpy Scraper Module.

Uses the jobspy library to scrape jobs from multiple sources including:
indeed, linkedin, zip_recruiter, google, glassdoor, bayt, naukri, bdjobs
"""
import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import settings

from scrapers.common import ScraperBase
from schemas.job import JobListing


class JobSpyScraper(ScraperBase):
    """Scraper using jobspy library for multiple job sources."""

    NAME = "jobspy"

    def __init__(self):
        """Initialize the JobSpy scraper."""
        super().__init__()

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs using jobspy library.

        Args:
            query: Search query (skills/roles)
            location: Optional location filter
            max_results: Maximum results to return

        Returns:
            List of raw job data dictionaries
        """
        # Run the synchronous jobspy function in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            df = await loop.run_in_executor(
                None,  # Use default executor
                self._scrape_jobs_sync,
                query,
                location,
                max_results
            )
            
            # Convert DataFrame to list of dictionaries
            jobs = []
            if df is not None and not df.empty:
                # Select and rename columns to match our schema
                for _, row in df.iterrows():
                    job = self._convert_jobspy_row_to_dict(row)
                    if job:
                        jobs.append(job)
                        
            return jobs[:max_results]
        except Exception as e:
            print(f"[JobSpy] Error scraping jobs: {e}")
            return []

    def _scrape_jobs_sync(
        self,
        query: str,
        location: Optional[str],
        max_results: int
    ):
        """Synchronous scraping function to run in executor."""
        from jobspy import scrape_jobs
        
        # Prepare search parameters
        search_term = query if query else "software engineer"
        google_search_term = None
        
        # If location is provided and not empty, create a google search term
        if location and location.strip():
            google_search_term = f"{search_term} jobs near {location.strip()} since yesterday"
        
        # Determine which sites to use - explicitly request multiple sources
        site_name = ["indeed", "linkedin", "zip_recruiter", "google"]
        
        # Prepare country_indeed parameter - only set to 'USA' if location is provided and contains 'usa'
        # Otherwise use jobspy's default
        country_indeed = 'USA' if location and location.strip() and 'usa' in location.lower() else 'usa'
        
        try:
            jobs_df = scrape_jobs(
                site_name=site_name,
                search_term=search_term,
                google_search_term=google_search_term,
                location=location.strip() if location and location.strip() else None,
                results_wanted=max_results,
                hours_old=72,  # Jobs from last 72 hours
                country_indeed=country_indeed,
                # linkedin_fetch_description=False  # Set to True for more info but slower
            )
            return jobs_df
        except Exception as e:
            print(f"[JobSpy] scrape_jobs error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _convert_jobspy_row_to_dict(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Convert a jobspy DataFrame row to our job dictionary format."""
        try:
            # Extract job ID - jobspy provides job_id or we can create one
            job_id = str(row.get('job_id', ''))
            if not job_id or job_id == 'nan':
                # Create a hash from title, company, and location if no job_id
                import hashlib
                job_string = f"{row.get('title', '')}{row.get('company', '')}{row.get('location', '')}"
                job_id = hashlib.md5(job_string.encode()).hexdigest()[:12]
            
            # Extract apply URL - jobspy provides job_url
            apply_url = row.get('job_url')
            if pd.isna(apply_url) or not apply_url:
                apply_url = None
                
            # Extract salary - combine min and max if available
            salary_range = None
            min_amount = row.get('min_amount')
            max_amount = row.get('max_amount')
            currency = row.get('currency', 'USD')
            interval = row.get('interval', 'yearly')
            
            if not pd.isna(min_amount) or not pd.isna(max_amount):
                min_str = f"{min_amount:.0f}" if not pd.isna(min_amount) else ""
                max_str = f"{max_amount:.0f}" if not pd.isna(max_amount) else ""
                if min_str and max_str:
                    salary_range = f"{currency} {min_str} - {max_str} {interval}"
                elif min_str:
                    salary_range = f"{currency} {min_str}+ {interval}"
                elif max_str:
                    salary_range = f"{currency} Up to {max_str} {interval}"
                else:
                    salary_range = f"{currency} {interval}"
            
            # Extract job type
            job_type = row.get('job_type')
            if pd.isna(job_type) or not job_type:
                job_type = None
            else:
                # Normalize job type
                job_type = str(job_type).lower().strip()
                if 'full' in job_type:
                    job_type = 'Full-time'
                elif 'part' in job_type:
                    job_type = 'Part-time'
                elif 'contract' in job_type or 'temp' in job_type:
                    job_type = 'Contract'
                elif 'intern' in job_type:
                    job_type = 'Internship'
                else:
                    job_type = job_type.title()
            
            # Extract description
            description = row.get('description')
            if pd.isna(description) or not description:
                description = ""
            else:
                # Limit description length
                description = str(description)[:1000]
            
            # Extract posted date
            posted_date = None
            date_posted = row.get('date_posted')
            if not pd.isna(date_posted):
                try:
                    if isinstance(date_posted, str):
                        posted_date = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
                    elif hasattr(date_posted, 'year') and hasattr(date_posted, 'month') and hasattr(date_posted, 'day'):
                        # Handle date objects (convert to datetime at midnight)
                        if isinstance(date_posted, datetime):
                            posted_date = date_posted
                        else:
                            # It's a date object, convert to datetime
                            posted_date = datetime.combine(date_posted, datetime.min.time())
                    # Handle timestamp
                    elif isinstance(date_posted, (int, float)):
                        posted_date = datetime.fromtimestamp(date_posted)
                except Exception as e:
                    print(f"[JobSpy] Error parsing date {date_posted}: {e}")
                    posted_date = None
            
            # Determine source - jobspy doesn't always provide this clearly
            # We'll infer from the site or use 'jobspy' as default
            source = row.get('site', 'jobspy')
            if pd.isna(source) or not source:
                source = 'jobspy'
            
            return {
                "id": job_id,
                "title": str(row.get('title', 'Unknown Position')),
                "company": str(row.get('company', 'Unknown Company')),
                "location": str(row.get('location', 'Unknown')),
                "description": description,
                "apply_url": apply_url,
                "source": source.lower(),
                "is_active": True,  # Assume active if scraped recently
                "posted_date": posted_date,
                "salary_range": salary_range,
                "job_type": job_type,
                "scraped_at": datetime.utcnow(),
            }
        except Exception as e:
            print(f"[JobSpy] Error converting row: {e}")
            return None


# Test function
async def test_jobspy_scraper():
    """Test the JobSpy scraper."""
    async with JobSpyScraper() as scraper:
        print(f"Testing JobSpy scraper")
        
        jobs = await scraper.search_jobs(
            query="Python developer",
            location="San Francisco, CA",
            max_results=10
        )
        
        print(f"Found {len(jobs)} jobs")
        
        for job in jobs[:3]:
            print(f"  - {job['title']} at {job['company']} ({job['location']})")
            print(f"    Source: {job['source']}, Salary: {job.get('salary_range', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_jobspy_scraper())