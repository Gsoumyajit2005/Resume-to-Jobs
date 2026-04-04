"""
Job Matcher Service.

Handles matching resumes to jobs using:
1. Heuristic pre-filtering (skills overlap)
2. LLM-based scoring (detailed analysis)
"""
import asyncio
from typing import List, Dict, Any, Optional

from services.cache import get_cache
from chains.job_match_chain import get_match_chain, JobMatchingChain
from schemas.match import MatchedJob, MatchResponse, HeuristicMatch
from schemas.resume import ResumeData
from schemas.job import JobListing
from utils.text_utils import TextUtils
from config import settings


class JobMatcher:
    """
    Service for matching resumes to jobs.

    Uses a two-stage approach:
    1. Heuristic filtering (fast, based on skills)
    2. LLM scoring (slow, detailed analysis)
    """

    def __init__(self, chain: Optional[JobMatchingChain] = None):
        """
        Initialize the matcher.

        Args:
            chain: Optional JobMatchingChain instance
        """
        self._chain = chain or get_match_chain()
        self._cache = get_cache()

    async def match_resume_to_jobs(
        self,
        resume_data: ResumeData,
        jobs: List[JobListing]
    ) -> MatchResponse:
        """
        Match a resume to a list of jobs.

        Args:
            resume_data: Parsed resume data
            jobs: List of job listings

        Returns:
            MatchResponse with ranked jobs
        """
        start_time = asyncio.get_event_loop().time()

        # Step 1: Heuristic pre-filtering
        heuristic_matches = self._compute_heuristic_matches(resume_data, jobs)

        # Step 2: Sort by heuristic score and limit for LLM scoring
        heuristic_matches.sort(key=lambda x: x.score, reverse=True)
        top_jobs = heuristic_matches[:settings.MAX_JOBS_FOR_LLM_SCORING]

        # Step 3: LLM scoring on top jobs
        llm_scores = await self._compute_llm_scores(resume_data, top_jobs)

        # Step 4: Combine scores and sort
        final_matches = self._combine_scores(heuristic_matches, llm_scores)

        # Step 5: Build response
        matched_jobs = []
        for match in final_matches:
            # Find original job
            original_job = next(
                (j for j in jobs if j.id == match.job_id),
                None
            )

            if original_job:
                matched_jobs.append(MatchedJob(
                    job_id=match.job_id,
                    match_score=match.match_score,
                    reason=match.reason,
                    matched_skills=match.matched_skills,
                    missing_skills=match.missing_skills,
                    heuristic_score=match.heuristic_score,
                    job=original_job.model_dump()
                ))

        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return MatchResponse(
            total_matches=len(matched_jobs),
            matched_jobs=matched_jobs,
            processing_time_ms=processing_time
        )

    def _compute_heuristic_matches(
        self,
        resume_data: ResumeData,
        jobs: List[JobListing]
    ) -> List[HeuristicMatch]:
        """
        Compute heuristic match scores.

        Uses simple rules:
        - Skills overlap percentage
        - Role keyword matching
        - Location proximity

        Args:
            resume_data: Parsed resume data
            jobs: List of job listings

        Returns:
            List of HeuristicMatch objects
        """
        matches = []

        resume_skills = set(s.lower() for s in resume_data.skills)
        resume_roles = set(r.lower() for r in resume_data.preferred_roles)

        for job in jobs:
            # Extract skills from job description
            job_description = (job.description + " " + job.title + " " + job.location).lower()

            # Count skill matches
            matched_skills = []
            missing_skills = []

            for skill in resume_skills:
                if skill in job_description:
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)

            # Calculate overlap percentage
            if resume_skills:
                overlap_pct = (len(matched_skills) / len(resume_skills)) * 100
            else:
                overlap_pct = 0

            # Role matching bonus
            role_match_bonus = 0
            for role in resume_roles:
                if role in job_description:
                    role_match_bonus = 10
                    break

            # Calculate final heuristic score
            base_score = int(overlap_pct * 0.8)
            final_score = min(100, base_score + role_match_bonus)

            matches.append(HeuristicMatch(
                job_id=job.id,
                score=final_score,
                skills_matched=matched_skills,
                skills_missing=missing_skills,
                skill_overlap_percentage=round(overlap_pct, 2)
            ))

        return matches

    async def _compute_llm_scores(
        self,
        resume_data: ResumeData,
        jobs: List[JobListing]
    ) -> List[dict]:
        """
        Compute detailed LLM scores for jobs.

        Args:
            resume_data: Parsed resume data
            jobs: List of JobListing objects to score

        Returns:
            List of LLM match score dictionaries
        """
        # Build resume context for LLM
        resume_context = {
            "name": resume_data.name,
            "skills": resume_data.skills,
            "experience": resume_data.experience[:3],
            "education": resume_data.education,
            "preferred_roles": resume_data.preferred_roles,
            "total_experience_years": resume_data.total_experience_years
        }

        llm_scores = []
        for job in jobs:
            description = f"{job.title}\n{job.company}\n{job.description}"
            score = await self._chain.score_job(resume_context, description)

            llm_scores.append({
                "job_id": job.id,
                "match_score": score.match_score,
                "reason": score.reason,
                "matched_skills": score.matched_skills,
                "missing_skills": score.missing_skills
            })

        return llm_scores

    def _combine_scores(
        self,
        heuristic_matches: List[HeuristicMatch],
        llm_scores: List[dict]
    ) -> List[dict]:
        """
        Combine heuristic and LLM scores.

        Uses weighted average:
        - Heuristic: 30%
        - LLM: 70%

        Args:
            heuristic_matches: Heuristic match results
            llm_scores: LLM match results

        Returns:
            Combined match results
        """
        # Create LLM score lookup
        llm_lookup = {s["job_id"]: s for s in llm_scores}

        combined = []

        for match in heuristic_matches:
            llm_score_data = llm_lookup.get(match.job_id)
            if llm_score_data:
                # Weighted average
                final_score = int(
                    match.score * 0.3 + llm_score_data["match_score"] * 0.7
                )
                reason = llm_score_data["reason"]
                # Ensure skills are lists (LLM might return as string)
                llm_matched = llm_score_data.get("matched_skills", [])
                llm_missing = llm_score_data.get("missing_skills", [])
                if isinstance(llm_matched, str):
                    llm_matched = [llm_matched] if llm_matched else []
                if isinstance(llm_missing, str):
                    llm_missing = [llm_missing] if llm_missing else []
                matched_skills = llm_matched if llm_matched else match.skills_matched
                missing_skills = llm_missing if llm_missing else match.skills_missing
            else:
                # No LLM score, use heuristic only
                final_score = match.score
                reason = f"Matched on {len(match.skills_matched)} skills."
                matched_skills = match.skills_matched
                missing_skills = match.skills_missing

            combined.append({
                "job_id": match.job_id,
                "match_score": final_score,
                "reason": reason,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "heuristic_score": match.score
            })

        # Sort by match score
        combined.sort(key=lambda x: x["match_score"], reverse=True)

        return combined

    async def match_resume_to_jobs_full(
        self,
        resume_data: ResumeData,
        jobs: List[JobListing]
    ) -> MatchResponse:
        """
        Complete matching pipeline.

        This is the corrected version that properly passes job objects to LLM.

        Args:
            resume_data: Parsed resume data
            jobs: List of job listings

        Returns:
            MatchResponse with ranked jobs
        """
        start_time = asyncio.get_event_loop().time()

        # Heuristic pre-filtering
        heuristic_matches = self._compute_heuristic_matches(resume_data, jobs)
        heuristic_matches.sort(key=lambda x: x.score, reverse=True)

        # Limit for LLM scoring
        top_matches = heuristic_matches[:settings.MAX_JOBS_FOR_LLM_SCORING]

        # Build resume context
        resume_context = {
            "name": resume_data.name,
            "skills": resume_data.skills,
            "experience": resume_data.experience[:3],
            "education": resume_data.education,
            "preferred_roles": resume_data.preferred_roles,
            "total_experience_years": resume_data.total_experience_years
        }

        # Create jobs lookup
        jobs_lookup = {job.id: job for job in jobs}

        # LLM scoring
        llm_scores = []
        for match in top_matches:
            job = jobs_lookup.get(match.job_id)
            if job:
                description = f"{job.title}\n{job.company}\n{job.description}"
                score = await self._chain.score_job(resume_context, description)

                llm_scores.append({
                    "job_id": match.job_id,
                    "match_score": score.match_score,
                    "reason": score.reason,
                    "matched_skills": score.matched_skills,
                    "missing_skills": score.missing_skills
                })

        # Combine scores
        combined = self._combine_scores(heuristic_matches, llm_scores)

        # Build response
        matched_jobs = []
        for match in combined:
            job = jobs_lookup.get(match["job_id"])
            if job:
                matched_jobs.append(MatchedJob(
                    job_id=match["job_id"],
                    match_score=match["match_score"],
                    reason=match["reason"],
                    matched_skills=match["matched_skills"],
                    missing_skills=match["missing_skills"],
                    heuristic_score=match["heuristic_score"],
                    job=job.model_dump()
                ))

        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return MatchResponse(
            total_matches=len(matched_jobs),
            matched_jobs=matched_jobs,
            processing_time_ms=processing_time
        )


# Global instance
_matcher: Optional[JobMatcher] = None


def get_job_matcher() -> JobMatcher:
    """
    Get or create a global job matcher instance.

    Returns:
        JobMatcher instance
    """
    global _matcher
    if _matcher is None:
        _matcher = JobMatcher()
    return _matcher
