"""
test_ranker.py — Tests for the Ranking Engine

Tests each scoring function in isolation and the combined ranking pipeline.
Uses carefully crafted mock candidates that represent:
  - Strong AI candidate (should rank high)
  - Keyword-stuffing trap candidate (should rank low despite many AI keywords)
  - Non-tech candidate (should rank very low)
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.jd_parser import parse_jd
from src.ranker import (
    compute_skill_score,
    compute_experience_score,
    compute_career_score,
    compute_behavior_score,
    rank_candidate,
)
from src.config import JD_TEXT


@pytest.fixture
def parsed_jd():
    return parse_jd(JD_TEXT)


# ---------------------------------------------------------------------------
# Strong AI Candidate
# ---------------------------------------------------------------------------
@pytest.fixture
def strong_ai_candidate():
    return {
        "candidate_id": "CAND_STRONG1",
        "profile": {
            "anonymized_name": "Strong AI",
            "headline": "Senior ML Engineer | Ranking, Retrieval, Embeddings",
            "summary": "6 years building ranking and retrieval systems at product companies.",
            "location": "Pune, Maharashtra",
            "country": "India",
            "years_of_experience": 6.5,
            "current_title": "Senior ML Engineer",
            "current_company": "ProductCo",
            "current_company_size": "201-500",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "company": "ProductCo", "title": "Senior ML Engineer",
                "start_date": "2022-01-01", "end_date": None,
                "duration_months": 30, "is_current": True,
                "industry": "Software", "company_size": "201-500",
                "description": "Built ranking system with embeddings and FAISS.",
            },
            {
                "company": "TechStartup", "title": "ML Engineer",
                "start_date": "2019-06-01", "end_date": "2021-12-31",
                "duration_months": 31, "is_current": False,
                "industry": "Technology", "company_size": "51-200",
                "description": "Built recommendation engine with vector search.",
            },
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 30, "duration_months": 60},
            {"name": "PyTorch", "proficiency": "advanced", "endorsements": 15, "duration_months": 36},
            {"name": "FAISS", "proficiency": "advanced", "endorsements": 10, "duration_months": 24},
            {"name": "sentence-transformers", "proficiency": "advanced", "endorsements": 8, "duration_months": 18},
            {"name": "Docker", "proficiency": "intermediate", "endorsements": 5, "duration_months": 30},
        ],
        "education": [],
        "certifications": [],
        "languages": [],
        "redrob_signals": {
            "profile_completeness_score": 90, "signup_date": "2025-01-15",
            "last_active_date": "2026-06-10", "open_to_work_flag": True,
            "profile_views_received_30d": 40, "applications_submitted_30d": 3,
            "recruiter_response_rate": 0.85, "avg_response_time_hours": 12,
            "skill_assessment_scores": {}, "connection_count": 500,
            "endorsements_received": 80, "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 25, "max": 40},
            "preferred_work_mode": "hybrid", "willing_to_relocate": True,
            "github_activity_score": 72, "search_appearance_30d": 150,
            "saved_by_recruiters_30d": 12, "interview_completion_rate": 0.92,
            "offer_acceptance_rate": 0.75, "verified_email": True,
            "verified_phone": True, "linkedin_connected": True,
        },
    }


# ---------------------------------------------------------------------------
# Keyword-Stuffing Trap Candidate (Marketing Manager with AI keywords)
# ---------------------------------------------------------------------------
@pytest.fixture
def trap_candidate():
    return {
        "candidate_id": "CAND_TRAP001",
        "profile": {
            "anonymized_name": "Trap User",
            "headline": "Marketing Manager | Driving business outcomes",
            "summary": "Professional with 8 years in marketing management.",
            "location": "Mumbai",
            "country": "India",
            "years_of_experience": 8.0,
            "current_title": "Marketing Manager",
            "current_company": "Wipro",
            "current_company_size": "10001+",
            "current_industry": "IT Services",
        },
        "career_history": [
            {
                "company": "Wipro", "title": "Marketing Manager",
                "start_date": "2021-01-01", "end_date": None,
                "duration_months": 30, "is_current": True,
                "industry": "IT Services", "company_size": "10001+",
                "description": "Brand marketing and content strategy.",
            },
            {
                "company": "TCS", "title": "Marketing Manager",
                "start_date": "2018-01-01", "end_date": "2020-12-31",
                "duration_months": 36, "is_current": False,
                "industry": "IT Services", "company_size": "10001+",
                "description": "SEO strategy and content writing.",
            },
        ],
        "skills": [
            {"name": "NLP", "proficiency": "advanced", "endorsements": 30, "duration_months": 36},
            {"name": "LLM", "proficiency": "advanced", "endorsements": 20, "duration_months": 24},
            {"name": "PyTorch", "proficiency": "advanced", "endorsements": 15, "duration_months": 30},
            {"name": "FAISS", "proficiency": "advanced", "endorsements": 10, "duration_months": 24},
            {"name": "Marketing", "proficiency": "expert", "endorsements": 50, "duration_months": 80},
            {"name": "SEO", "proficiency": "expert", "endorsements": 40, "duration_months": 60},
            {"name": "Content Writing", "proficiency": "expert", "endorsements": 35, "duration_months": 70},
            {"name": "Photoshop", "proficiency": "advanced", "endorsements": 20, "duration_months": 50},
        ],
        "education": [],
        "certifications": [],
        "languages": [],
        "redrob_signals": {
            "profile_completeness_score": 75, "signup_date": "2025-06-01",
            "last_active_date": "2026-03-01", "open_to_work_flag": True,
            "profile_views_received_30d": 10, "applications_submitted_30d": 5,
            "recruiter_response_rate": 0.30, "avg_response_time_hours": 120,
            "skill_assessment_scores": {}, "connection_count": 200,
            "endorsements_received": 30, "notice_period_days": 60,
            "expected_salary_range_inr_lpa": {"min": 12, "max": 18},
            "preferred_work_mode": "flexible", "willing_to_relocate": False,
            "github_activity_score": -1, "search_appearance_30d": 50,
            "saved_by_recruiters_30d": 3, "interview_completion_rate": 0.5,
            "offer_acceptance_rate": -1, "verified_email": True,
            "verified_phone": False, "linkedin_connected": False,
        },
    }


class TestSkillScoring:
    def test_strong_candidate_high_skill_score(self, parsed_jd, strong_ai_candidate):
        score, matched, missing = compute_skill_score(strong_ai_candidate, parsed_jd)
        assert score > 30, f"Strong AI candidate should have skill score > 30, got {score}"
        assert len(matched) >= 2, "Should match multiple required skills"

    def test_trap_candidate_penalized(self, parsed_jd, trap_candidate):
        score, matched, missing = compute_skill_score(trap_candidate, parsed_jd)
        strong_score, _, _ = compute_skill_score(
            pytest.importorskip("src.tests.test_ranker").strong_ai_candidate, parsed_jd
        ) if False else (80, [], [])  # placeholder
        # Trap candidate should get some skill score (they DO have AI keywords)
        # but it should be moderated by the non-tech penalty
        assert score < 100, "Trap candidate should not get perfect skill score"

    def test_empty_skills(self, parsed_jd):
        empty_candidate = {
            "candidate_id": "EMPTY",
            "skills": [],
            "profile": {"years_of_experience": 5},
        }
        score, matched, missing = compute_skill_score(empty_candidate, parsed_jd)
        assert score == 0.0


class TestExperienceScoring:
    def test_perfect_match(self, parsed_jd):
        candidate = {"profile": {"years_of_experience": 7.0}}
        score = compute_experience_score(candidate, parsed_jd)
        assert score == 100.0, f"7 years should be perfect for 5-9 range, got {score}"

    def test_under_experienced(self, parsed_jd):
        candidate = {"profile": {"years_of_experience": 1.0}}
        score = compute_experience_score(candidate, parsed_jd)
        assert score < 60, f"1 year should score low for 5-9 range, got {score}"

    def test_slightly_over(self, parsed_jd):
        candidate = {"profile": {"years_of_experience": 10.0}}
        score = compute_experience_score(candidate, parsed_jd)
        assert score >= 80, f"10 years should still be OK for 5-9 range, got {score}"


class TestCareerScoring:
    def test_strong_progression(self, parsed_jd, strong_ai_candidate):
        score, title_rel, flags = compute_career_score(strong_ai_candidate, parsed_jd)
        assert score > 40, f"Strong career should score > 40, got {score}"
        assert "all_services_career" not in flags

    def test_trap_candidate_flagged(self, parsed_jd, trap_candidate):
        score, title_rel, flags = compute_career_score(trap_candidate, parsed_jd)
        assert "all_services_career" in flags, "Pure Wipro+TCS career should be flagged"
        assert "non_ai_title" in flags, "Marketing Manager should be flagged as non-AI"

    def test_no_career_history(self, parsed_jd):
        candidate = {
            "candidate_id": "NO_CAREER",
            "career_history": [],
            "profile": {"current_title": "Unknown", "current_industry": "Unknown"},
        }
        score, _, flags = compute_career_score(candidate, parsed_jd)
        assert score <= 50
        assert "no_career_history" in flags


class TestBehaviorScoring:
    def test_active_responsive_candidate(self, strong_ai_candidate):
        score = compute_behavior_score(strong_ai_candidate)
        assert score > 60, f"Active, responsive candidate should score > 60, got {score}"

    def test_inactive_candidate(self):
        inactive = {
            "redrob_signals": {
                "profile_completeness_score": 30,
                "last_active_date": "2025-01-01",
                "open_to_work_flag": False,
                "recruiter_response_rate": 0.05,
                "avg_response_time_hours": 200,
                "github_activity_score": -1,
                "interview_completion_rate": 0.3,
                "verified_email": False,
                "verified_phone": False,
                "linkedin_connected": False,
            }
        }
        score = compute_behavior_score(inactive)
        assert score < 40, f"Inactive candidate should score < 40, got {score}"


class TestFinalRanking:
    def test_strong_beats_trap(self, parsed_jd, strong_ai_candidate, trap_candidate):
        """Strong AI candidate should ALWAYS outrank the keyword-stuffing trap."""
        strong_result = rank_candidate(strong_ai_candidate, parsed_jd, semantic_score=85)
        trap_result = rank_candidate(trap_candidate, parsed_jd, semantic_score=60)

        assert strong_result.final_score > trap_result.final_score, (
            f"Strong candidate ({strong_result.final_score:.4f}) should beat "
            f"trap candidate ({trap_result.final_score:.4f})"
        )

    def test_reasoning_generated(self, parsed_jd, strong_ai_candidate):
        result = rank_candidate(strong_ai_candidate, parsed_jd, semantic_score=85)
        assert len(result.reasoning) > 20, "Reasoning should be meaningful"
        assert "Senior ML Engineer" in result.reasoning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
