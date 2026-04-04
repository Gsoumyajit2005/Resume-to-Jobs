"""
Common Scraper Utilities.

Shared functionality for all scrapers including:
- HTTP client configuration
- Retry logic
- Rate limiting
- Anti-blocking measures
"""
import asyncio
import random
import time
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import httpx
from bs4 import BeautifulSoup

from config import settings


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class ScraperHTTPError(ScraperError):
    """HTTP-related scraper errors."""
    pass


class ScraperTimeoutError(ScraperError):
    """Timeout-related scraper errors."""
    pass


class RateLimiter:
    """
    Rate limiter for scraping requests.

    Implements token bucket algorithm for rate limiting.
    """

    def __init__(self, requests_per_second: float = 0.5):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
        """
        self.requests_per_second = requests_per_second
        self.min_delay = 1.0 / requests_per_second
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until we can make a request."""
        async with self._lock:
            elapsed = time.monotonic() - self._last_request_time
            if elapsed < self.min_delay:
                wait_time = self.min_delay - elapsed + random.uniform(0.1, 0.5)
                await asyncio.sleep(wait_time)
            self._last_request_time = time.monotonic()


class ScraperBase:
    """
    Base class for all scrapers.

    Provides common functionality:
    - HTTP client with retry logic
    - Header rotation
    - Rate limiting
    - Error handling
    """

    NAME: str = "base"
    BASE_URL: str = ""
    HEADERS: Dict[str, str] = {}

    def __init__(self):
        """Initialize the scraper with a configured HTTP client."""
        self.rate_limiter = RateLimiter(requests_per_second=0.3)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_client()

    async def _create_client(self) -> httpx.AsyncClient:
        """Create and configure the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=settings.get_headers(),
                timeout=httpx.Timeout(
                    connect=settings.REQUEST_TIMEOUT,
                    read=settings.REQUEST_TIMEOUT,
                    write=settings.REQUEST_TIMEOUT,
                    pool=settings.REQUEST_TIMEOUT
                ),
                follow_redirects=True,
                verify=True
            )
        return self._client

    async def _close_client(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _get_page(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        retries: int = settings.RETRY_COUNT
    ) -> Optional[str]:
        """
        Fetch a page with retry logic and rate limiting.

        Args:
            url: URL to fetch
            params: Query parameters
            retries: Number of retry attempts

        Returns:
            HTML content as string, or None if all retries fail
        """
        for attempt in range(retries):
            try:
                # Apply rate limiting
                await self.rate_limiter.acquire()

                if not self._client:
                    await self._create_client()

                response = await self._client.get(
                    url,
                    params=params,
                    headers=settings.get_headers()
                )

                if response.status_code == 200:
                    return response.text

                elif response.status_code == 403:
                    # Rate limited, wait longer
                    await asyncio.sleep(2 ** attempt * random.uniform(1, 3))

                elif response.status_code >= 500:
                    # Server error, retry
                    await asyncio.sleep(2 ** attempt * random.uniform(0.5, 2))

                else:
                    # Client error, don't retry
                    raise ScraperHTTPError(
                        f"HTTP {response.status_code} for {url}"
                    )

            except httpx.TimeoutException:
                if attempt == retries - 1:
                    raise ScraperTimeoutError(
                        f"Timeout fetching {url} after {retries} attempts"
                    )
                await asyncio.sleep(2 ** attempt * random.uniform(0.5, 2))

            except (httpx.NetworkError, httpx.ProtocolError) as e:
                if attempt == retries - 1:
                    raise ScraperHTTPError(
                        f"Network error fetching {url}: {str(e)}"
                    )
                await asyncio.sleep(2 ** attempt * random.uniform(0.5, 2))

        return None

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML into BeautifulSoup object."""
        return BeautifulSoup(html, "lxml")

    def _check_job_active(
        self,
        job_data: Dict[str, Any]
    ) -> bool:
        """
        Check if a job listing appears to be active.

        Args:
            job_data: Parsed job data

        Returns:
            True if job appears active
        """
        # If apply URL is missing, likely inactive
        apply_url = job_data.get("apply_url")
        if not apply_url:
            return False

        # If no description, likely inactive
        description = job_data.get("description", "")
        if not description or len(description) < 50:
            return False

        return True

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs matching the query.

        Must be implemented by subclasses.

        Args:
            query: Search query (skills/roles)
            location: Optional location filter
            max_results: Maximum results to return

        Returns:
            List of raw job data dictionaries
        """
        raise NotImplementedError

    async def validate_apply_url(self, url: str) -> bool:
        """
        Check if an apply URL is valid (returns 200).

        Args:
            url: Apply URL to check

        Returns:
            True if URL is valid
        """
        try:
            if not self._client:
                await self._create_client()

            response = await self._client.head(url, follow_redirects=True)
            return response.status_code == 200

        except Exception:
            return False

    @classmethod
    def get_source_name(cls) -> str:
        """Get the source name for this scraper."""
        return cls.NAME
