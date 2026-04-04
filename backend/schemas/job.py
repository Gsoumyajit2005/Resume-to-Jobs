"""
Job Listing Schemas.

Defines Pydantic models for job listings from various sources.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class JobListing(BaseModel):
    """
    Standardized job listing schema.

    All scrapers normalize their output to this schema.
    """
    id: str = Field(
        ...,
        description="Unique identifier for the job (source-specific)"
    )
    title: str = Field(
        ...,
        description="Job title"
    )
    company: str = Field(
        ...,
        description="Company name"
    )
    location: str = Field(
        ...,
        description="Job location (can include remote/hybrid)"
    )
    description: str = Field(
        ...,
        description="Job description text"
    )
    apply_url: Optional[str] = Field(
        None,
        description="URL to apply for the job"
    )
    source: str = Field(
        ...,
        description="Source of the job (e.g., 'indeed', 'remoteok')"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the job is currently active/available"
    )
    posted_date: Optional[datetime] = Field(
        None,
        description="When the job was posted"
    )
    salary_range: Optional[str] = Field(
        None,
        description="Salary information if available"
    )
    job_type: Optional[str] = Field(
        None,
        description="Full-time, contract, part-time, etc."
    )
    scraped_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the job was scraped"
    )

    class Config:
        extra = "ignore"
        strict = True
        json_schema_extra = {
            "example": {
                "id": "job_12345",
                "title": "Senior Software Engineer",
                "company": "Tech Corporation",
                "location": "San Francisco, CA (Remote friendly)",
                "description": "We are looking for an experienced software engineer...",
                "apply_url": "https://techcorp.com/careers/job12345",
                "source": "indeed",
                "is_active": True,
                "posted_date": "2026-03-15T00:00:00Z",
                "salary_range": "$150,000 - $180,000",
                "job_type": "Full-time",
                "scraped_at": "2026-04-03T10:00:00Z"
            }
        }


class JobSearchRequest(BaseModel):
    """Request model for searching jobs."""
    role: Optional[str] = Field(
        None,
        description="Job title or role to search for"
    )
    location: Optional[str] = Field(
        None,
        description="Job location"
    )
    skills: Optional[List[str]] = Field(
        None,
        description="Skills to filter by (from resume)"
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "Software Engineer",
                "location": "San Francisco",
                "skills": ["Python", "JavaScript", "React"],
                "max_results": 25
            }
        }


class JobSearchResponse(BaseModel):
    """Response model for job search."""
    total_jobs: int
    jobs: List[JobListing]
    query: JobSearchRequest

    class Config:
        json_schema_extra = {
            "example": {
                "total_jobs": 25,
                "query": JobSearchRequest.Config.json_schema_extra["example"],
                "jobs": [JobListing.Config.json_schema_extra["example"]]
            }
        }


class JobStats(BaseModel):
    """Statistics about job listings."""
    total_count: int
    active_count: int
    by_source: dict[str, int]
    by_location: dict[str, int]
    by_job_type: dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "total_count": 100,
                "active_count": 95,
                "by_source": {"indeed": 45, "remoteok": 30, "linkedin": 25},
                "by_location": {"San Francisco": 30, "Remote": 25, "New York": 20},
                "by_job_type": {"Full-time": 70, "Contract": 20, "Part-time": 5}
            }
        }
