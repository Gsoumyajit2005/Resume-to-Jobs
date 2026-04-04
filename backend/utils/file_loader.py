"""
File Loading Utilities.

Handles loading and text extraction from PDF and DOCX files.
"""
import io
import re
from typing import Optional
from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document


class FileLoader:
    """Utility class for loading and extracting text from resume files."""

    @staticmethod
    def load_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(file_path)
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            return "\n".join(text_parts)

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def load_docx(file_path: str) -> str:
        """
        Extract text from a DOCX file.

        Args:
            file_path: Path to the DOCX file

        Returns:
            Extracted text content
        """
        try:
            doc = Document(file_path)

            # Extract text from paragraphs
            paragraphs = [para.text for para in doc.paragraphs]

            # Extract text from tables
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    cell_texts = [cell.text for cell in row.cells]
                    tables_text.append(" ".join(cell_texts))

            all_text = "\n".join(paragraphs + tables_text)
            return FileLoader._clean_text(all_text)

        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    @staticmethod
    def load_bytes(file_content: bytes, file_type: str) -> str:
        """
        Extract text from file bytes based on file type.

        Args:
            file_content: Raw file bytes
            file_type: 'pdf' or 'docx'

        Returns:
            Extracted text content
        """
        if file_type.lower() == "pdf":
            return FileLoader._load_pdf_bytes(file_content)
        elif file_type.lower() == "docx":
            return FileLoader._load_docx_bytes(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _load_pdf_bytes(file_content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            reader = PdfReader(io.BytesIO(file_content))
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            return "\n".join(text_parts)

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF bytes: {str(e)}")

    @staticmethod
    def _load_docx_bytes(file_content: bytes) -> str:
        """Extract text from DOCX bytes."""
        try:
            doc = Document(io.BytesIO(file_content))

            paragraphs = [para.text for para in doc.paragraphs]
            tables_text = []

            for table in doc.tables:
                for row in table.rows:
                    cell_texts = [cell.text for cell in row.cells]
                    tables_text.append(" ".join(cell_texts))

            all_text = "\n".join(paragraphs + tables_text)
            return FileLoader._clean_text(all_text)

        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX bytes: {str(e)}")

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean extracted text by normalizing whitespace.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove multiple consecutive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace from each line
        text = "\n".join(line.strip() for line in text.split("\n"))

        return text.strip()

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get file extension without the dot."""
        return Path(file_path).suffix.lower().lstrip(".")
