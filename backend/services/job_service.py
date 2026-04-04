"""
Job Service.

Handles job scraping, aggregation, filtering, and search.
"""
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from scrapers.indeed import IndeedScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.remoteok import RemoteOKScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper
from scrapers.jobspy_scraper import JobSpyScraper
from scrapers.common import ScraperError
from services.cache import get_cache
from schemas.job import JobListing, JobSearchResponse, JobSearchRequest
from config import settings


class JobService:
    """
    Service for job scraping and management.

    Coordinates multiple scrapers and provides:
    - Parallel scraping
    - Job deduplication
    - Active job filtering
    - Caching
    """

    def __init__(self):
        """Initialize the job service with configured scrapers."""
        self._cache = get_cache()
        self._scrapers = {
            "weworkremotely": WeWorkRemotelyScraper(),
            "remoteok": RemoteOKScraper(),
            "indeed": IndeedScraper(),
            "linkedin": LinkedInScraper(),
            "jobspy": JobSpyScraper(),
        }
        self._enabled_sources = settings.ENABLED_SOURCES

    async def search_jobs(
        self,
        query: JobSearchRequest
    ) -> JobSearchResponse:
        """
        Search for jobs based on query parameters.

        Args:
            query: JobSearchRequest with search parameters

        Returns:
            JobSearchResponse with matched jobs
        """
        # Check cache first
        search_hash = self._generate_search_hash(query)
        cached = await self._cache.get_job_search(search_hash)
        if cached:
            return JobSearchResponse(
                total_jobs=len(cached),
                jobs=[JobListing(**job) for job in cached],
                query=query
            )

        # Fetch jobs from all enabled sources in parallel
        jobs = await self._fetch_jobs_parallel(query)

        # Deduplicate jobs
        jobs = self._deduplicate_jobs(jobs)

        # Filter to active jobs
        jobs = self._filter_active_jobs(jobs)

        # Sort by posting date (newest first)
        jobs = self._sort_jobs(jobs)

        # Limit results
        jobs = jobs[:query.max_results]

        # Save to cache
        await self._cache.save_job_search(search_hash, [j.model_dump() for j in jobs])

        return JobSearchResponse(
            total_jobs=len(jobs),
            jobs=jobs,
            query=query
        )

    async def _fetch_jobs_parallel(self, query: JobSearchRequest) -> List[JobListing]:
        """
        Fetch jobs from multiple sources in parallel.

        Args:
            query: JobSearchRequest

        Returns:
            List of all job listings
        """
        tasks = []
        for source in self._enabled_sources:
            scraper = self._scrapers.get(source)
            if scraper:
                tasks.append(self._fetch_from_source(scraper, query))

        # Run all scrapers in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results, skipping any scraper errors
        all_jobs = []
        source_names = [s for s in self._enabled_sources if self._scrapers.get(s)]
        for idx, result in enumerate(results):
            if isinstance(result, list):
                all_jobs.extend(result)

        return all_jobs

    async def _fetch_from_source(
        self,
        scraper,
        query: JobSearchRequest
    ) -> List[JobListing]:
        """
        Fetch jobs from a single scraper.

        Args:
            scraper: Scraper instance
            query: JobSearchRequest

        Returns:
            List of job listings from that source
        """
        max_per_source = settings.MAX_JOBS_PER_SOURCE

        # Build query string from role and skills
        query_parts = [query.role] if query.role else []
        if query.skills:
            query_parts.extend(query.skills[:3])  # Limit to top 3 skills
        search_query = " ".join(query_parts) if query_parts else "software engineer"

        # Handle location - convert empty string or "None" to None for jobspy
        location = query.location
        if location == "" or location == "None":
            location = None

        print(f"[JobService] Fetching from {scraper.NAME}: query='{search_query}', location='{location}'")

        raw_jobs = await scraper.search_jobs(
            query=search_query,
            location=location,
            max_results=max_per_source
        )

        # Debug: print number of raw jobs found
        print(f"[JobService] {scraper.NAME} found {len(raw_jobs)} raw jobs")

        # Convert to JobListing schema
        jobs = []
        for raw in raw_jobs:
            try:
                job = JobListing(**raw)
                jobs.append(job)
            except Exception as e:
                # Skip malformed job entries
                print(f"[JobService] Error converting job: {e}")
                continue

        print(f"[JobService] {scraper.NAME} converted to {len(jobs)} valid jobs")
        return jobs

    def _generate_search_hash(self, query: JobSearchRequest) -> str:
        """
        Generate a cache key hash for search parameters.

        Args:
            query: JobSearchRequest

        Returns:
            SHA256 hash string
        """
        search_str = f"{query.role}:{query.location}:{query.skills}:{query.max_results}"
        return hashlib.sha256(search_str.encode()).hexdigest()[:16]

    def _deduplicate_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """
        Remove duplicate job listings.

        Args:
            jobs: List of job listings

        Returns:
            Deduplicated list
        """
        seen = set()
        unique_jobs = []

        for job in jobs:
            # Create dedup key from title + company + location
            dedup_key = f"{job.title.lower()}|{job.company.lower()}|{job.location.lower()}"

            if dedup_key not in seen:
                seen.add(dedup_key)
                unique_jobs.append(job)

        return unique_jobs

    def _filter_active_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """
        Filter to only active jobs.

        A job is considered active if:
        - is_active flag is True
        - posted_date is within threshold
        - apply_url is present and valid

        Args:
            jobs: List of job listings

        Returns:
            Filtered list of active jobs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=settings.JOB_AGE_DAYS_THRESHOLD)

        active_jobs = []

        for job in jobs:
            # Check is_active flag
            if not job.is_active:
                continue

            # Check posting date
            if job.posted_date and job.posted_date < cutoff_date:
                continue

            # Check apply URL exists
            if not job.apply_url:
                continue

            # Quick URL validity check
            if not self._is_valid_url(job.apply_url):
                continue

            active_jobs.append(job)

        return active_jobs

    def _is_valid_url(self, url: str) -> bool:
        """
        Basic URL validity check.

        Args:
            url: URL to check

        Returns:
            True if URL appears valid
        """
        if not url:
            return False

        # Basic checks
        if not url.startswith(("http://", "https://")):
            return False

        if len(url) > 2048:
            return False

        return True

    def _sort_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """
        Sort jobs by posting date (newest first).

        Args:
            jobs: List of job listings

        Returns:
            Sorted list
        """
        def sort_key(job: JobListing):
            if job.posted_date:
                return job.posted_date
            return datetime.min  # Put unknown dates at end

        return sorted(jobs, key=sort_key, reverse=True)

    async def get_job_by_id(self, job_id: str, source: str) -> Optional[JobListing]:
        """
        Get a specific job by ID.

        Args:
            job_id: Job ID
            source: Source (e.g., 'indeed', 'remoteok')

        Returns:
            JobListing or None if not found
        """
        # This would require source-specific lookup
        # For now, return None (jobs are not stored individually)
        return None

    async def get_job_stats(self) -> dict:
        """
        Get statistics about cached jobs.

        Returns:
            Dictionary with job statistics
        """
        # Get all cached job searches
        stats = {
            "total_jobs": 0,
            "by_source": {},
            "by_location": {},
        }

        return stats


# Global instance
_service: Optional[JobService] = None


def get_job_service() -> JobService:
    """
    Get or create a global job service instance.

    Returns:
        JobService instance
    """
    global _service
    if _service is None:
        _service = JobService()
    return _service
