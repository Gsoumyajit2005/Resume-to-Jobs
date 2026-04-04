"""
Resume Parsing Chain.

LangChain-based pipeline for extracting structured resume data from raw text.
Uses LLM with structured output for reliable parsing.
"""
from typing import List, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from config import RESUME_EXTRACTION_PROMPT, settings


class ResumeSkills(BaseModel):
    """Schema for skills extraction."""
    skills: List[str] = Field(description="List of technical skills and programming languages")


class ResumeExperienceItem(BaseModel):
    """Schema for a single experience entry."""
    company: str = Field(description="Company name")
    role: str = Field(description="Job title")
    duration: str = Field(description="Duration at company")
    responsibilities: str = Field(description="Key responsibilities and achievements")


class ResumeEducationItem(BaseModel):
    """Schema for a single education entry."""
    institution: str = Field(description="Educational institution name")
    degree: str = Field(description="Degree earned")
    year: str = Field(description="Year of graduation or attendance")


class ParsedResume(BaseModel):
    """Structured output schema for resume parsing."""
    name: str = Field(description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="Location")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn URL")
    github: Optional[str] = Field(default=None, description="GitHub URL")
    skills: List[str] = Field(description="List of technical skills")
    experience: List[str] = Field(description="List of work experiences")
    education: List[str] = Field(description="List of education entries")
    projects: List[str] = Field(description="List of projects")
    summary: Optional[str] = Field(default=None, description="Professional summary")
    preferred_roles: List[str] = Field(
        description="Inferred job titles the candidate is suited for"
    )
    total_experience_years: Optional[float] = Field(
        default=None,
        description="Total years of experience calculated"
    )


class ResumeParsingChain:
    """
    LangChain-based resume parsing pipeline.

    Takes raw resume text and outputs structured ResumeData.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-6", temperature: float = 0.3):
        """
        Initialize the resume parsing chain.

        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature for LLM randomness
        """
        self.model_name = model_name
        self.temperature = temperature
        self._chain = None

    def _create_chain(self):
        """Create and compile the LangChain pipeline."""
        # Create the LLM instance
        llm_kwargs = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": 2000,
            "timeout": 60,
        }

        # Add custom endpoint if configured (for local/K8s models)
        if settings.LLM_BASE_URL:
            llm_kwargs["base_url"] = settings.LLM_BASE_URL.rstrip("/")
            llm_kwargs["api_key"] = settings.LLM_API_KEY

        llm = ChatOpenAI(**llm_kwargs)

        # Create prompt template from config
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESUME_EXTRACTION_PROMPT),
            ("user", "{resume_text}")
        ])

        # Create the chain using LCEL
        chain = prompt | llm | JsonOutputParser(pydantic_object=ParsedResume)

        return chain

    def get_chain(self):
        """Get or create the chain instance."""
        if self._chain is None:
            self._chain = self._create_chain()
        return self._chain

    async def parse_resume(self, resume_text: str) -> ParsedResume:
        """
        Parse a resume from raw text into structured data.

        Args:
            resume_text: Raw text extracted from the resume file

        Returns:
            ParsedResume with structured data
        """
        chain = self.get_chain()

        # Clean and truncate text if too long
        max_length = 15000  # Token limit headroom
        if len(resume_text) > max_length:
            resume_text = resume_text[:max_length]
            # Try to cut at a sentence boundary
            last_period = resume_text.rfind(".")
            if last_period > max_length * 0.9:
                resume_text = resume_text[:last_period + 1]

        try:
            result = await chain.ainvoke({"resume_text": resume_text})
            # JsonOutputParser returns a dict, convert to ParsedResume
            return ParsedResume(**result)
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from response
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse resume: {str(e)}")

    async def extract_skills(self, resume_text: str) -> List[str]:
        """
        Extract just the skills list from a resume.

        Args:
            resume_text: Raw resume text

        Returns:
            List of skills
        """
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=1000,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract only the technical skills, programming languages, and tools from the resume text. Return as a JSON list of strings."),
            ("user", "Resume: {text}")
        ])

        chain = prompt | llm | JsonOutputParser(pydantic_object=ResumeSkills)

        try:
            result = await chain.ainvoke({"text": resume_text[:5000]})
            return result["skills"]
        except Exception:
            return []

    def batch_parse_resumes(self, texts: List[str]) -> List[ParsedResume]:
        """
        Parse multiple resumes in batch.

        Args:
            texts: List of raw resume texts

        Returns:
            List of ParsedResume objects
        """
        # Sequential for simplicity - could be parallelized
        return [self.parse_resume(text) for text in texts]


# Global chain instance for reuse
_resume_chain: Optional[ResumeParsingChain] = None


def get_resume_chain() -> ResumeParsingChain:
    """
    Get or create a global resume parsing chain instance.

    Returns:
        ResumeParsingChain instance
    """
    global _resume_chain
    if _resume_chain is None:
        # Use model name from config, or default to config value
        from config import settings
        _resume_chain = ResumeParsingChain(model_name=settings.LLM_MODEL_NAME)
    return _resume_chain
