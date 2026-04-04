"""
Resume Parsing Chain.

LangChain-based pipeline for extracting structured resume data from raw text.
Uses LLM with structured output for reliable parsing.
"""
from typing import List, Optional
import json

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from config import RESUME_EXTRACTION_PROMPT, settings
import re
import re


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
            "api_key": settings.GROQ_API_KEY,
        }

        llm = ChatGroq(**llm_kwargs)

        # Create prompt template from config
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESUME_EXTRACTION_PROMPT + "\n\nIMPORTANT: Return ONLY valid JSON. Do NOT include any thinking tags, explanations, or additional text. Start your response directly with the JSON object."),
            ("user", "{resume_text}")
        ])

        # Create the chain using LCEL with string output parser for manual JSON extraction
        chain = prompt | llm | StrOutputParser()

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
            raw_response = await chain.ainvoke({"resume_text": resume_text})
            
            # Debug: print raw response to see what we're getting
            print(f"[ResumeChain] Raw LLM response: {raw_response[:200]}...")
            
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
                return ParsedResume(**result)
            else:
                raise ValueError("No JSON object found in LLM response")
        except json.JSONDecodeError as e:
            print(f"[ResumeChain] JSON decode error: {e}")
            print(f"[ResumeChain] Problematic JSON: {json_str if 'json_str' in locals() else 'N/A'}")
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
        llm = ChatGroq(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=1000,
            api_key=settings.GROQ_API_KEY,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract only the technical skills, programming languages, and tools from the resume text. Return as a JSON list of strings."),
            ("user", "Resume: {text}")
        ])

        chain = prompt | llm | StrOutputParser()

        try:
            raw_response = await chain.ainvoke({"text": resume_text[:5000]})
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result.get("skills", result) if isinstance(result, dict) else result
            return []
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
