"""
test_jd_parser.py — Tests for the JD Understanding Engine

Tests skill extraction, experience parsing, seniority detection,
hidden requirements inference, and the full parse pipeline.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.jd_parser import parse_jd, _extract_experience, _extract_seniority
from src.config import JD_TEXT


class TestExperienceExtraction:
    """Test experience year parsing from various JD formats."""

    def test_range_format(self):
        """5-9 years → (5.0, 9.0)"""
        result = _extract_experience("Looking for 5-9 years of experience")
        assert result[0] == 5.0
        assert result[1] == 9.0

    def test_plus_format(self):
        """5+ years → (5.0, 15.0)"""
        result = _extract_experience("Requires 5+ years experience")
        assert result[0] == 5.0
        assert result[1] == 15.0

    def test_minimum_format(self):
        """minimum 3 years → (3.0, 13.0)"""
        result = _extract_experience("Minimum 3 years of experience required")
        assert result[0] == 3.0

    def test_no_experience_mentioned(self):
        """No experience → (0.0, 99.0)"""
        result = _extract_experience("Join our team as a developer")
        assert result[0] == 0.0
        assert result[1] == 99.0

    def test_em_dash_range(self):
        """5–9 years (em dash)"""
        result = _extract_experience("Experience Required: 5\u20139 years")
        assert result[0] == 5.0
        assert result[1] == 9.0


class TestSeniorityDetection:
    """Test seniority level detection from JD text."""

    def test_senior(self):
        label, level = _extract_seniority("Senior AI Engineer")
        assert label == "senior"
        assert level == 4

    def test_lead(self):
        label, level = _extract_seniority("Lead Machine Learning Engineer")
        assert label == "lead"
        assert level == 5

    def test_junior(self):
        label, level = _extract_seniority("Junior Developer position")
        assert label == "junior"
        assert level == 2

    def test_default_mid(self):
        label, level = _extract_seniority("Software Developer needed")
        assert level == 3


class TestFullParsing:
    """Test the complete parse_jd pipeline on the actual JD."""

    @pytest.fixture
    def parsed(self):
        return parse_jd(JD_TEXT)

    def test_role_extracted(self, parsed):
        """Should extract a meaningful role title."""
        assert parsed.role != "Unknown Role"
        assert len(parsed.role) > 5

    def test_seniority_is_senior(self, parsed):
        """JD is for Senior AI Engineer."""
        assert parsed.seniority_level >= 4

    def test_experience_range(self, parsed):
        """JD says 5-9 years."""
        assert parsed.experience_min >= 4
        assert parsed.experience_max <= 15

    def test_required_skills_not_empty(self, parsed):
        """Should extract multiple required skills."""
        assert len(parsed.required_skills) >= 3

    def test_python_is_required(self, parsed):
        """JD explicitly requires strong Python."""
        assert "python" in parsed.required_skills

    def test_hidden_requirements_exist(self, parsed):
        """Should infer hidden requirements."""
        assert len(parsed.hidden_requirements) >= 1

    def test_locations_extracted(self, parsed):
        """JD mentions Pune and Noida."""
        location_lower = [l.lower() for l in parsed.location_preferences]
        assert "pune" in location_lower or "noida" in location_lower

    def test_negative_signals(self, parsed):
        """JD explicitly warns against pure services backgrounds."""
        assert len(parsed.negative_signals) >= 1

    def test_output_dict(self, parsed):
        """to_dict should produce valid JSON-serializable dict."""
        d = parsed.to_dict()
        assert "role" in d
        assert "required_skills" in d
        assert "hidden_requirements" in d
        assert isinstance(d["required_skills"], list)


class TestSkillExtraction:
    """Test skill extraction from various JD formats."""

    def test_simple_jd(self):
        jd = "Looking for a Python developer with experience in Docker and AWS."
        parsed = parse_jd(jd)
        skills_lower = [s.lower() for s in parsed.required_skills]
        assert "python" in skills_lower
        assert "docker" in skills_lower

    def test_ai_jd(self):
        jd = """
        Senior AI Engineer with 5+ years experience in
        Python, LLMs, Retrieval Systems, Vector Databases and
        Production AI deployment.
        """
        parsed = parse_jd(jd)
        assert len(parsed.required_skills) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
