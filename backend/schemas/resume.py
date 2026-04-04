"""
Resume Data Schemas.

Defines Pydantic models for structured resume data extraction.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    """
    Structured representation of a resume after LLM extraction.

    This schema is used internally after parsing the raw resume text
    through the LangChain extraction pipeline.
    """
    name: str = Field(
        ...,
        description="Candidate's full name"
    )
    email: Optional[str] = Field(
        None,
        description="Candidate's email address"
    )
    phone: Optional[str] = Field(
        None,
        description="Candidate's phone number"
    )
    location: Optional[str] = Field(
        None,
        description="Candidate's location/city"
    )
    linkedin: Optional[str] = Field(
        None,
        description="LinkedIn profile URL"
    )
    github: Optional[str] = Field(
        None,
        description="GitHub profile URL"
    )
    skills: List[str] = Field(
        ...,
        description="List of technical skills, programming languages, and tools"
    )
    experience: List[str] = Field(
        ...,
        description="List of work experiences with company names and key responsibilities"
    )
    education: List[str] = Field(
        ...,
        description="List of educational qualifications"
    )
    projects: List[str] = Field(
        ...,
        description="List of notable projects with descriptions"
    )
    summary: Optional[str] = Field(
        None,
        description="Professional summary or objective"
    )
    preferred_roles: List[str] = Field(
        ...,
        description="Inferred job titles the candidate is suited for"
    )
    total_experience_years: Optional[float] = Field(
        None,
        description="Calculated total years of experience"
    )
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the resume was extracted"
    )

    class Config:
        extra = "ignore"
        strict = True
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "location": "San Francisco, CA",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
                "experience": [
                    "Senior Software Engineer at TechCorp (2020-2024) - Led backend team, architected microservices",
                    "Software Developer at Startup Inc (2018-2020) - Built full-stack web applications"
                ],
                "education": [
                    "MS in Computer Science, University of Tech (2016-2018)",
                    "BS in Software Engineering, State University (2012-2016)"
                ],
                "projects": [
                    "Project Alpha: A distributed task scheduler using Kubernetes and Go"
                ],
                "summary": "Senior software engineer with 6+ years of experience in full-stack development.",
                "preferred_roles": ["Senior Software Engineer", "Backend Engineer", "Tech Lead"],
                "total_experience_years": 6.5,
                "extracted_at": "2026-04-03T10:00:00Z"
            }
        }


class ResumeUploadResponse(BaseModel):
    """Response after successfully uploading and parsing a resume."""
    message: str
    resume_id: str
    extracted_data: ResumeData

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Resume successfully processed",
                "resume_id": "res_abc123def456",
                "extracted_data": ResumeData.Config.json_schema_extra
            }
        }
