"""
Resume Parser Service.

Handles file loading, text extraction, and LLM-based resume parsing.
"""
import asyncio
from typing import Optional, Dict, Any, List

from services.cache import get_cache
from chains.resume_chain import get_resume_chain, ResumeParsingChain
from utils.file_loader import FileLoader
from schemas.resume import ResumeData, ResumeUploadResponse


class ResumeParser:
    """
    Service for parsing resumes from uploaded files.

    Handles:
    - File upload and validation
    - Text extraction from PDF/DOCX
    - LLM-based structured extraction
    - Caching of results
    """

    def __init__(self, chain: Optional[ResumeParsingChain] = None):
        """
        Initialize the parser.

        Args:
            chain: Optional ResumeParsingChain instance (uses default if not provided)
        """
        self._chain = chain or get_resume_chain()
        self._cache = get_cache()

    async def parse_file(
        self,
        file_path: str,
        file_content: Optional[bytes] = None,
        file_type: Optional[str] = None
    ) -> ResumeUploadResponse:
        """
        Parse a resume file and extract structured data.

        Args:
            file_path: Path to the file
            file_content: Optional raw file bytes
            file_type: 'pdf', 'docx', or None for automatic detection

        Returns:
            ResumeUploadResponse with parsed data
        """
        # Determine file type from extension if not provided
        if file_type is None:
            file_type = FileLoader.get_file_extension(file_path)

        if file_type not in ("pdf", "docx"):
            raise ValueError(f"Unsupported file type: {file_type}. Must be PDF or DOCX.")

        # Load text from file
        if file_content:
            text = FileLoader.load_bytes(file_content, file_type)
        else:
            text = FileLoader.load_pdf(file_path) if file_type == "pdf" else FileLoader.load_docx(file_path)

        if not text.strip():
            raise ValueError("No text could be extracted from the file.")

        # Generate unique ID for this resume
        resume_id = await self._cache.generate_id("res")

        # Try to get from cache first
        cached = await self._cache.get_parsed_resume(resume_id)
        if cached:
            return ResumeUploadResponse(
                message="Resume loaded from cache",
                resume_id=resume_id,
                extracted_data=cached
            )

        # Parse with LLM
        parsed_resume = await self._chain.parse_resume(text)

        # Convert to ResumeData schema
        resume_data = ResumeData(
            name=parsed_resume.name,
            email=parsed_resume.email,
            phone=parsed_resume.phone,
            location=parsed_resume.location,
            linkedin=parsed_resume.linkedin,
            github=parsed_resume.github,
            skills=parsed_resume.skills,
            experience=parsed_resume.experience,
            education=parsed_resume.education,
            projects=parsed_resume.projects,
            summary=parsed_resume.summary,
            preferred_roles=parsed_resume.preferred_roles,
            total_experience_years=parsed_resume.total_experience_years
        )

        # Save to cache
        await self._cache.save_parsed_resume(resume_id, resume_data.model_dump())

        return ResumeUploadResponse(
            message="Resume successfully processed",
            resume_id=resume_id,
            extracted_data=resume_data
        )

    async def parse_text(
        self,
        resume_text: str,
        resume_id: Optional[str] = None
    ) -> ResumeUploadResponse:
        """
        Parse resume from raw text.

        Args:
            resume_text: Raw text content of the resume
            resume_id: Optional existing ID (generates new if not provided)

        Returns:
            ResumeUploadResponse with parsed data
        """
        if not resume_text.strip():
            raise ValueError("Resume text cannot be empty.")

        if resume_id is None:
            resume_id = await self._cache.generate_id("res")

        # Try cache
        cached = await self._cache.get_parsed_resume(resume_id)
        if cached:
            return ResumeUploadResponse(
                message="Resume loaded from cache",
                resume_id=resume_id,
                extracted_data=cached
            )

        # Parse with LLM
        parsed_resume = await self._chain.parse_resume(resume_text)

        resume_data = ResumeData(
            name=parsed_resume.name,
            email=parsed_resume.email,
            phone=parsed_resume.phone,
            location=parsed_resume.location,
            linkedin=parsed_resume.linkedin,
            github=parsed_resume.github,
            skills=parsed_resume.skills,
            experience=parsed_resume.experience,
            education=parsed_resume.education,
            projects=parsed_resume.projects,
            summary=parsed_resume.summary,
            preferred_roles=parsed_resume.preferred_roles,
            total_experience_years=parsed_resume.total_experience_years
        )

        await self._cache.save_parsed_resume(resume_id, resume_data.model_dump())

        return ResumeUploadResponse(
            message="Resume successfully processed",
            resume_id=resume_id,
            extracted_data=resume_data
        )

    async def get_parsed_resume(self, resume_id: str) -> Optional[ResumeData]:
        """
        Retrieve a previously parsed resume.

        Args:
            resume_id: The ID of the parsed resume

        Returns:
            ResumeData or None if not found
        """
        cached = await self._cache.get_parsed_resume(resume_id)
        if cached:
            return ResumeData(**cached)
        return None

    async def extract_skills(self, resume_text: str) -> List[str]:
        """
        Extract skills from resume text (quick extraction without full parsing).

        Args:
            resume_text: Raw resume text

        Returns:
            List of skills
        """
        return await self._chain.extract_skills(resume_text)


# Global instance
_parser: Optional[ResumeParser] = None


def get_resume_parser() -> ResumeParser:
    """
    Get or create a global resume parser instance.

    Returns:
        ResumeParser instance
    """
    global _parser
    if _parser is None:
        _parser = ResumeParser()
    return _parser
