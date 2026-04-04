"""
Configuration module for Resume-to-Jobs Matching Platform.

Contains all constants, thresholds, and configuration values
for the application.
"""
from typing import List, Dict, Any
import os


# === Application Settings ===
class Settings:
    """Application settings and configuration."""

    # Scraping thresholds
    JOB_AGE_DAYS_THRESHOLD: int = 30
    MAX_PARALLEL_SCRAPERS: int = 3
    MAX_JOBS_PER_SOURCE: int = 20
    MAX_JOBS_FOR_LLM_SCORING: int = 50

    # Anti-blocking measures
    REQUEST_TIMEOUT: int = 15
    RETRY_COUNT: int = 3
    SCRAPING_DELAY_MIN: float = 1.0
    SCRAPING_DELAY_MAX: float = 3.0

    # LLM Configuration
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "claude-sonnet-4-6")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")  # Custom endpoint for local/K8s
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "dummy")  # Required even for local models
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2000

    # API Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Job sources to scrape
    ENABLED_SOURCES: List[str] = ["weworkremotely"]  # Use WeWorkRemotely which has simple HTML

    # Header rotation for anti-blocking
    USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get rotated headers for scraping."""
        import random
        return {
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }


settings = Settings()


# === LangChain Prompt Templates ===
RESUME_EXTRACTION_PROMPT = """
You are an expert resume parser. Extract structured information from the provided resume text.

Instructions:
1. Extract all relevant information about the candidate
2. For skills, identify technical skills, programming languages, tools, and frameworks
3. For experience, list job titles, companies, and key responsibilities
4. For education, extract degrees, institutions, and dates
5. For projects, list notable projects with descriptions
6. For preferred roles, infer likely job titles based on experience

Return a valid JSON object with the following structure:
- name: string (candidate's full name)
- skills: array of strings (technical skills)
- experience: array of strings (job descriptions or achievements)
- education: array of strings (education details)
- projects: array of strings (project descriptions)
- preferred_roles: array of strings (likely job titles)

Resume Text:
{resume_text}

Return ONLY the JSON object, no other text.
"""

JOB_MATCH_PROMPT = """
You are a job matching expert. Analyze how well a candidate's resume matches a job description.

Input:
- Resume Data: Contains candidate's skills, experience, education, and preferred roles
- Job Description: The job posting details

Your task:
1. Analyze skills match between resume and job requirements
2. Consider experience relevance
3. Evaluate education fit
4. Consider role alignment

Output a JSON object with:
- match_score: integer 0-100 (how well the candidate matches)
- reason: string (1-2 sentence explanation of the match)
- matched_skills: array of strings (skills from resume that match the job)
- missing_skills: array of strings (skills in job that are missing from resume)

Resume Data:
{resume_data}

Job Description:
{job_description}

Return ONLY the JSON object, no other text.
"""


# === Pydantic Models Configuration ===
PYDANTIC_CONFIG = {
    "extra": "ignore",
    "strict": True,
}
