"""
Job Matching Chain.

LangChain-based pipeline for scoring job-candidate matches.
Uses LLM with structured output for reliable scoring.
"""
from typing import List, Optional
import json

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from config import JOB_MATCH_PROMPT, settings
import re
import re


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
            "api_key": settings.GROQ_API_KEY,
        }

        llm = ChatGroq(**llm_kwargs)

        prompt = ChatPromptTemplate.from_messages([
            ("system", JOB_MATCH_PROMPT + "\n\nIMPORTANT: Return ONLY valid JSON. Do NOT include any thinking tags, explanations, or additional text. Start your response directly with the JSON object."),
            ("user", "Resume Data: {resume_data}\n\nJob Description: {job_description}")
        ])

        chain = prompt | llm | StrOutputParser()

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
            raw_response = await chain.ainvoke({
                "resume_data": json.dumps(resume_data),
                "job_description": job_description
            })
            
            # Debug: print raw response to see what we're getting
            print(f"[JobMatchChain] Raw LLM response: {raw_response[:200]}...")
            
            # Extract JSON from response - try multiple patterns
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                # Try to find JSON between triple backticks
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
            if not json_match:
                # Try to find JSON after thinking tags
                json_match = re.search(r'<\|begin\|><\|assistant\|>.*?(\{.*\})', raw_response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1) if json_match.lastindex else json_match.group(0)
                # Clean up the JSON string
                json_str = json_str.strip()
                result = json.loads(json_str)
                return MatchScore(**result)
            else:
                raise ValueError("No JSON object found in LLM response")
        except json.JSONDecodeError as e:
            print(f"[JobMatchChain] JSON decode error: {e}")
            print(f"[JobMatchChain] Problematic JSON: {json_str if 'json_str' in locals() else 'N/A'}")
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
