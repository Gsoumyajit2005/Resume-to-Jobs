"""
Text Processing Utilities.

Provides helper functions for text normalization, scoring, and analysis.
"""
import re
import string
from typing import List, Set, Tuple, Optional
from collections import Counter


class TextUtils:
    """Utility class for text processing operations."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.

        Converts to lowercase, removes extra whitespace,
        and strips punctuation.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text
        """
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text.

        Filters out common words and short tokens.

        Args:
            text: Input text
            min_length: Minimum word length to include

        Returns:
            List of keywords
        """
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Common words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'we', 'they', 'what', 'which', 'who', 'whom', 'whose', 'where',
            'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'also'
        }

        words = text.lower().split()
        keywords = [
            word for word in words
            if len(word) >= min_length and word not in stop_words
        ]

        return keywords

    @staticmethod
    def calculate_keyword_overlap(
        text1: str,
        text2: str
    ) -> Tuple[List[str], float]:
        """
        Calculate keyword overlap between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Tuple of (matched keywords, overlap percentage)
        """
        keywords1 = set(TextUtils.extract_keywords(text1))
        keywords2 = set(TextUtils.extract_keywords(text2))

        if not keywords1 or not keywords2:
            return [], 0.0

        intersection = keywords1 & keywords2
        union = keywords1 | keywords2

        overlap = len(intersection) / len(union) if union else 0.0

        return list(intersection), round(overlap * 100, 2)

    @staticmethod
    def find_skills_in_text(
        skills_list: List[str],
        text: str
    ) -> Tuple[List[str], List[str]]:
        """
        Find which skills from a list appear in the text.

        Args:
            skills_list: List of skills to search for
            text: Text to search in

        Returns:
            Tuple of (matched skills, missing skills)
        """
        text_lower = text.lower()
        matched = []
        missing = []

        for skill in skills_list:
            skill_lower = skill.lower()
            # Check if skill appears in text (word boundary check)
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower) or skill_lower in text_lower:
                matched.append(skill)
            else:
                missing.append(skill)

        return matched, missing

    @staticmethod
    def calculate_skill_match_score(
        resume_skills: List[str],
        job_description: str
    ) -> dict:
        """
        Calculate a match score based on skills overlap.

        Args:
            resume_skills: List of skills from the resume
            job_description: Job description text

        Returns:
            Dictionary with score breakdown
        """
        matched, missing = TextUtils.find_skills_in_text(
            resume_skills, job_description
        )

        if not resume_skills:
            return {
                "score": 0,
                "matched": [],
                "missing": missing,
                "percentage": 0.0
            }

        score = int((len(matched) / len(resume_skills)) * 100)
        percentage = round((len(matched) / len(resume_skills)) * 100, 2)

        return {
            "score": score,
            "matched": matched,
            "missing": missing,
            "percentage": percentage
        }

    @staticmethod
    def extract_years_of_experience(text: str) -> Optional[float]:
        """
        Extract total years of experience from text.

        Looks for patterns like "5 years", "6+ years", etc.

        Args:
            text: Text to search in

        Returns:
            Total years as float, or None if not found
        """
        patterns = [
            r'(\d+)\s*\+\s*years?\s*of\s*experience',
            r'(\d+)\s*[-–]\s*(\d+)\s*years?\s*experience',
            r'(\d+)\s*years?\s*of\s*experience',
            r'(\d+)\s*years?\s*industy?',
        ]

        total_years = 0.0
        found_ranges = False

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Range like "5-10 years"
                    start, end = map(int, match)
                    total_years += (start + end) / 2
                    found_ranges = True
                else:
                    # Single number like "5 years"
                    total_years += float(match)

        return round(total_years, 1) if total_years > 0 else None

    @staticmethod
    def clean_html(text: str) -> str:
        """
        Remove HTML tags from text.

        Args:
            text: Text potentially containing HTML

        Returns:
            Clean text without HTML
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def truncate_text(text: str, max_length: int = 2000, ellipsis: str = "...") -> str:
        """
        Truncate text to max length, preserving word boundaries.

        Args:
            text: Input text
            max_length: Maximum length
            ellipsis: String to append if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        # Try to truncate at a word boundary
        truncated = text[:max_length - len(ellipsis)]
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + ellipsis
