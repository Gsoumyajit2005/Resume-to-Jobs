"""
Job Matching Chain.

LangChain-based pipeline for scoring job-candidate matches.
Uses LLM with structured output for reliable scoring.
"""
from typing import List, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from config import JOB_MATCH_PROMPT, settings


class MatchScore(BaseModel):
    """Schema for match scoring output."""
    match_score: int = Field(
        ge=0,
        le=100,
        description="Match score from 0-100"
    )
    reason: str = Field(
        description="1-2 sentence explanation of the match"
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills from resume that match the job"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills in job that are missing from resume"
    )


class JobMatchingChain:
    """
    LangChain-based job matching pipeline.

    Scores how well a candidate's resume matches a job description.
    """

    def __init__(self, model_name: str = None, temperature: float = 0.3):
        """
        Initialize the job matching chain.

        Args:
            model_name: Name of the LLM model to use (uses config default if None)
            temperature: Temperature for LLM randomness
        """
        self.model_name = model_name or settings.LLM_MODEL_NAME
        self.temperature = temperature
        self._chain = None

    def _create_chain(self):
        """Create and compile the LangChain pipeline."""
        llm_kwargs = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": 1000,
            "timeout": 60,
        }

        # Add custom endpoint if configured (for local/K8s models)
        if settings.LLM_BASE_URL:
            llm_kwargs["base_url"] = settings.LLM_BASE_URL.rstrip("/")
            llm_kwargs["api_key"] = settings.LLM_API_KEY

        llm = ChatOpenAI(**llm_kwargs)

        prompt = ChatPromptTemplate.from_messages([
            ("system", JOB_MATCH_PROMPT),
            ("user", "Resume Data: {resume_data}\n\nJob Description: {job_description}")
        ])

        chain = prompt | llm | JsonOutputParser(pydantic_object=MatchScore)

        return chain

    def get_chain(self):
        """Get or create the chain instance."""
        if self._chain is None:
            self._chain = self._create_chain()
        return self._chain

    async def score_job(
        self,
        resume_data: dict,
        job_description: str
    ) -> MatchScore:
        """
        Score how well a resume matches a job description.

        Args:
            resume_data: Dictionary containing resume information
            job_description: Job description text

        Returns:
            MatchScore with score and explanation
        """
        chain = self.get_chain()

        # Truncate job description if too long
        max_desc_length = 5000
        if len(job_description) > max_desc_length:
            job_description = job_description[:max_desc_length]
            last_period = job_description.rfind(".")
            if last_period > max_desc_length * 0.9:
                job_description = job_description[:last_period + 1]

        try:
            result = await chain.ainvoke({
                "resume_data": json.dumps(resume_data),
                "job_description": job_description
            })
            # JsonOutputParser returns a dict, convert to MatchScore
            return MatchScore(**result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

    async def batch_score_jobs(
        self,
        resume_data: dict,
        jobs: List[dict]
    ) -> List[MatchScore]:
        """
        Score multiple jobs against the same resume.

        Args:
            resume_data: Dictionary containing resume information
            jobs: List of job dictionaries

        Returns:
            List of MatchScore objects
        """
        results = []
        for job in jobs:
            description = job.get("description", "") + " " + job.get("title", "")
            score = await self.score_job(resume_data, description)
            results.append(score)
        return results


# Global chain instance
_match_chain: Optional[JobMatchingChain] = None


def get_match_chain() -> JobMatchingChain:
    """
    Get or create a global job matching chain instance.

    Returns:
        JobMatchingChain instance
    """
    global _match_chain
    if _match_chain is None:
        from config import settings
        _match_chain = JobMatchingChain(model_name=settings.LLM_MODEL_NAME)
    return _match_chain
