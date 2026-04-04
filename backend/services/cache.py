"""
In-Memory Cache Service.

Provides temporary storage for resumes, jobs, and matching results.
Uses a simple dictionary-based cache with expiration support.
"""
import asyncio
import time
import uuid
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CacheEntry:
    """A cache entry with expiration support."""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)  # 1 hour default

    @property
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return time.time() > self.expires_at

    def refresh(self, ttl: int = 3600) -> None:
        """Refresh the expiration time."""
        self.expires_at = time.time() + ttl


class ResumeCache:
    """
    In-memory cache for resume-related data.

    Stores:
    - Parsed resumes by ID
    - Job search results
    - Match scores
    """

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store a value in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        async with self._lock:
            if ttl is None:
                ttl = self._default_ttl

            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                expires_at=time.time() + ttl
            )

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired:
                del self._cache[key]
                return None

            return entry.value

    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    async def clear_all(self) -> None:
        """Clear all cached entries."""
        async with self._lock:
            self._cache.clear()

    # Resume-specific methods
    async def save_parsed_resume(
        self,
        resume_id: str,
        resume_data: dict,
        ttl: int = 3600
    ) -> None:
        """
        Save a parsed resume.

        Args:
            resume_id: Unique resume ID
            resume_data: Parsed resume data
            ttl: Time-to-live in seconds
        """
        await self.set(f"resume:{resume_id}", resume_data, ttl)

    async def get_parsed_resume(self, resume_id: str) -> Optional[dict]:
        """
        Get a parsed resume by ID.

        Args:
            resume_id: Unique resume ID

        Returns:
            Parsed resume data or None
        """
        return await self.get(f"resume:{resume_id}")

    # Job-related methods
    async def save_job_search(
        self,
        search_hash: str,
        jobs: List[dict],
        ttl: int = 1800  # 30 minutes for job listings
    ) -> None:
        """
        Save job search results.

        Args:
            search_hash: Hash of search parameters
            jobs: List of job dictionaries
            ttl: Time-to-live in seconds
        """
        await self.set(f"jobs:{search_hash}", jobs, ttl)

    async def get_job_search(self, search_hash: str) -> Optional[List[dict]]:
        """
        Get cached job search results.

        Args:
            search_hash: Hash of search parameters

        Returns:
            List of jobs or None
        """
        return await self.get(f"jobs:{search_hash}")

    # Match-related methods
    async def save_match_results(
        self,
        resume_id: str,
        match_results: List[dict],
        ttl: int = 3600
    ) -> None:
        """
        Save match results for a resume.

        Args:
            resume_id: Unique resume ID
            match_results: List of match score dictionaries
            ttl: Time-to-live in seconds
        """
        await self.set(f"matches:{resume_id}", match_results, ttl)

    async def get_match_results(self, resume_id: str) -> Optional[List[dict]]:
        """
        Get cached match results.

        Args:
            resume_id: Unique resume ID

        Returns:
            Match results or None
        """
        return await self.get(f"matches:{resume_id}")

    # Utility
    async def generate_id(self, prefix: str = "res") -> str:
        """
        Generate a unique ID.

        Args:
            prefix: Prefix for the ID

        Returns:
            Unique ID string
        """
        return f"{prefix}_{uuid.uuid4().hex[:12]}"


# Global cache instance
_cache: Optional[ResumeCache] = None


def get_cache() -> ResumeCache:
    """
    Get or create a global cache instance.

    Returns:
        ResumeCache instance
    """
    global _cache
    if _cache is None:
        _cache = ResumeCache()
    return _cache
