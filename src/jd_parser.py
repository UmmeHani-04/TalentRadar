"""
jd_parser.py — Job Description Understanding Engine

Phase 1 deliverable. Extracts structured information from raw JD text:
  - Role title and seniority level
  - Required and preferred skills
  - Experience requirements
  - Hidden/implied requirements (the "recruiter intuition" layer)
  - Industry context and keywords

Design choice: Hybrid regex + dictionary approach (no external LLM needed).
This runs offline and deterministically, which is critical for the challenge
constraint: "no network during ranking."

The key insight from the JD doc:
  "The right answer involves reasoning about the gap between what the JD says
   and what the JD means."
"""

import re
from dataclasses import dataclass, field

from src.utils.skills import normalize_skill, SKILL_ALIASES, SKILL_DOMAINS
from src.utils.mappings import (
    get_hidden_requirements,
    HIDDEN_REQUIREMENTS_MAP,
    get_title_seniority,
)


@dataclass
class ParsedJD:
    """Structured representation of a parsed Job Description."""
    role: str = ""
    seniority: str = ""                          # junior / mid / senior / lead / principal
    seniority_level: int = 3                     # 1-7 numeric
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    negative_signals: list[str] = field(default_factory=list)  # Skills/traits to avoid
    experience_min: float = 0.0
    experience_max: float = 99.0
    hidden_requirements: list[str] = field(default_factory=list)
    industry_keywords: list[str] = field(default_factory=list)
    location_preferences: list[str] = field(default_factory=list)
    jd_text: str = ""                            # Original text for embedding

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "seniority": self.seniority,
            "seniority_level": self.seniority_level,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "negative_signals": self.negative_signals,
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "hidden_requirements": self.hidden_requirements,
            "industry_keywords": self.industry_keywords,
            "location_preferences": self.location_preferences,
        }


# ---------------------------------------------------------------------------
# Seniority detection
# ---------------------------------------------------------------------------
SENIORITY_PATTERNS = {
    "intern":     (r'\b(?:intern|internship|trainee)\b', 1),
    "junior":     (r'\b(?:junior|jr\.?|entry[- ]level|associate)\b', 2),
    "mid":        (r'\b(?:mid[- ]?level|engineer|developer)\b', 3),
    "senior":     (r'\b(?:senior|sr\.?)\b', 4),
    "lead":       (r'\b(?:lead|staff|principal|tech lead|team lead)\b', 5),
    "director":   (r'\b(?:director|head of|vp|vice president)\b', 6),
    "executive":  (r'\b(?:cto|ceo|chief|c-level)\b', 7),
}


def _extract_seniority(text: str) -> tuple[str, int]:
    """Detect seniority level from JD text.

    Modifier keywords (junior, senior, lead, director, executive) take
    priority over base-title keywords (engineer, developer, mid-level)
    because 'Junior Developer' should resolve to 'junior', not 'mid'.
    """
    text_lower = text.lower()

    # Priority 1: explicit modifier keywords (these override everything)
    MODIFIER_LABELS = {"intern", "junior", "senior", "lead", "director", "executive"}
    best_modifier_level = 0
    best_modifier_label = None

    for label, (pattern, level) in SENIORITY_PATTERNS.items():
        if label in MODIFIER_LABELS and re.search(pattern, text_lower):
            if level > best_modifier_level:
                best_modifier_level = level
                best_modifier_label = label

    if best_modifier_label:
        return best_modifier_label, best_modifier_level

    # Priority 2: base-title keywords (fallback)
    best_level = 3  # default mid
    best_label = "mid"

    for label, (pattern, level) in SENIORITY_PATTERNS.items():
        if re.search(pattern, text_lower):
            if level > best_level:
                best_level = level
                best_label = label

    return best_label, best_level


# ---------------------------------------------------------------------------
# Experience extraction
# ---------------------------------------------------------------------------
EXPERIENCE_PATTERNS = [
    # "5-9 years" or "5–9 years"
    r'(\d+\.?\d*)\s*[-–—to]+\s*(\d+\.?\d*)\s*(?:\+?\s*)?year',
    # "5+ years"
    r'(\d+\.?\d*)\s*\+\s*year',
    # "at least 5 years" / "minimum 5 years"
    r'(?:at\s+least|minimum|min\.?)\s+(\d+\.?\d*)\s*year',
    # "5 years of experience"
    r'(\d+\.?\d*)\s*year[s]?\s*(?:of\s+)?experience',
]


def _extract_experience(text: str) -> tuple[float, float]:
    """Extract experience range from JD text. Returns (min, max)."""
    text_lower = text.lower()

    # Try range pattern first: "5-9 years"
    match = re.search(EXPERIENCE_PATTERNS[0], text_lower)
    if match:
        return float(match.group(1)), float(match.group(2))

    # "5+ years"
    match = re.search(EXPERIENCE_PATTERNS[1], text_lower)
    if match:
        min_exp = float(match.group(1))
        return min_exp, min_exp + 10  # Open-ended upper bound

    # "at least N years"
    match = re.search(EXPERIENCE_PATTERNS[2], text_lower)
    if match:
        min_exp = float(match.group(1))
        return min_exp, min_exp + 10

    # "N years of experience"
    match = re.search(EXPERIENCE_PATTERNS[3], text_lower)
    if match:
        years = float(match.group(1))
        return max(0, years - 2), years + 3  # Approximate range

    return 0.0, 99.0  # No experience mentioned


# ---------------------------------------------------------------------------
# Skill extraction
# ---------------------------------------------------------------------------
def _extract_skills(text: str) -> tuple[list[str], list[str]]:
    """Extract required and preferred skills from JD text.

    Scans the text for known skill names from the taxonomy, then classifies
    them as required vs preferred based on proximity to section headers.
    """
    text_lower = text.lower()
    found_skills = set()

    # Get all known canonical skill names from the alias map
    all_canonical_skills = set(SKILL_ALIASES.values())

    # Also check direct skill names from domains
    for domain_skills in SKILL_DOMAINS.values():
        all_canonical_skills.update(domain_skills)

    # Check for each known skill in the text
    for canonical in all_canonical_skills:
        # Check canonical name
        if re.search(r'\b' + re.escape(canonical) + r'\b', text_lower):
            found_skills.add(canonical)

    # Also check original alias keys (handles multi-word skill names)
    for alias, canonical in SKILL_ALIASES.items():
        if alias in text_lower:
            found_skills.add(canonical)

    # Classify into required vs preferred based on context
    required = set()
    preferred = set()

    # Split text into sections
    required_section = ""
    preferred_section = ""
    negative_section = ""

    # Look for section markers
    sections = re.split(
        r'(?i)(things you (?:absolutely )?need|required|must have|'
        r'things we\'?d like|preferred|nice to have|'
        r'things we (?:explicitly )?do not want|not looking for)',
        text
    )

    current_type = "required"  # Default: treat everything as required
    for section in sections:
        section_lower = section.lower()
        if re.search(r'(?:need|required|must)', section_lower):
            current_type = "required"
        elif re.search(r'(?:like|preferred|nice)', section_lower):
            current_type = "preferred"
        elif re.search(r'(?:not want|not looking)', section_lower):
            current_type = "negative"
        else:
            if current_type == "required":
                required_section += " " + section
            elif current_type == "preferred":
                preferred_section += " " + section
            else:
                negative_section += " " + section

    # Re-scan each section for skills
    for canonical in found_skills:
        in_negative = canonical in negative_section.lower() or any(
            alias in negative_section.lower()
            for alias, can in SKILL_ALIASES.items() if can == canonical
        )

        # Skills mentioned in the "do NOT want" section are excluded
        if in_negative:
            continue

        in_required = canonical in required_section.lower() or any(
            alias in required_section.lower()
            for alias, can in SKILL_ALIASES.items() if can == canonical
        )
        in_preferred = canonical in preferred_section.lower() or any(
            alias in preferred_section.lower()
            for alias, can in SKILL_ALIASES.items() if can == canonical
        )

        if in_required:
            required.add(canonical)
        elif in_preferred:
            preferred.add(canonical)
        else:
            required.add(canonical)  # Default to required if section unknown

    return sorted(required), sorted(preferred)


# ---------------------------------------------------------------------------
# Role title extraction
# ---------------------------------------------------------------------------
ROLE_PATTERNS = [
    r'(?:job\s+(?:title|description|role)\s*[:\-—]\s*)([^\n]+)',
    r'(?:position|role|title)\s*[:\-—]\s*([^\n]+)',
    r'(?:hiring|looking for)\s+(?:a\s+)?([^\n,\.]+)',
]


def _extract_role(text: str) -> str:
    """Extract the job role/title from JD text."""
    for pattern in ROLE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            role = match.group(1).strip()
            # Clean up: remove "at Company" suffixes
            role = re.sub(r'\s*[-–—]\s*(?:at|@)\s+.*$', '', role)
            # Remove trailing punctuation
            role = role.rstrip('.,;:')
            if len(role) < 100:  # Sanity check
                return role

    return "Unknown Role"


# ---------------------------------------------------------------------------
# Location extraction
# ---------------------------------------------------------------------------
def _extract_locations(text: str) -> list[str]:
    """Extract location preferences from JD text."""
    locations = []
    indian_cities = [
        "pune", "noida", "hyderabad", "mumbai", "bangalore", "bengaluru",
        "delhi", "gurgaon", "gurugram", "chennai", "kolkata",
    ]

    text_lower = text.lower()
    for city in indian_cities:
        if city in text_lower:
            locations.append(city.title())

    return locations


# ---------------------------------------------------------------------------
# Negative signal extraction
# ---------------------------------------------------------------------------
def _extract_negative_signals(text: str) -> list[str]:
    """Extract traits/signals the JD explicitly warns against."""
    signals = []
    text_lower = text.lower()

    negative_patterns = {
        "title_chaser": r"title[- ]?chaser|switching companies every",
        "framework_enthusiast": r"framework enthusiast",
        "pure_services": r"only worked at consulting|tcs|infosys|wipro|accenture|cognizant|capgemini",
        "pure_cv_speech": r"computer vision.*without.*nlp|speech.*without.*nlp|robotics.*without",
        "pure_research": r"pure research|academic labs|research-only",
        "no_recent_code": r"hasn't written.*code|moved into.*architecture",
    }

    for signal_name, pattern in negative_patterns.items():
        if re.search(pattern, text_lower):
            signals.append(signal_name)

    return signals


# ---------------------------------------------------------------------------
# Hidden requirements inference
# ---------------------------------------------------------------------------
def _infer_hidden_requirements(required_skills: list[str],
                                preferred_skills: list[str]) -> list[str]:
    """Infer hidden/implied requirements from the explicitly stated skills.

    This is the "recruiter intuition" layer — e.g., "production AI deployment"
    implies Docker, Kubernetes, CI/CD, Monitoring.
    """
    hidden = set()
    all_stated = set(required_skills + preferred_skills)

    for skill in all_stated:
        implied = get_hidden_requirements(skill)
        for imp in implied:
            if imp not in all_stated:
                hidden.add(imp)

    return sorted(hidden)


# ===========================================================================
# PUBLIC API
# ===========================================================================
def parse_jd(jd_text: str) -> ParsedJD:
    """Parse a raw Job Description into structured form.

    Args:
        jd_text: Raw JD text (can include markdown, bullet points, etc.)

    Returns:
        ParsedJD with all extracted fields populated.
    """
    role = _extract_role(jd_text)
    seniority, seniority_level = _extract_seniority(jd_text)
    exp_min, exp_max = _extract_experience(jd_text)
    required_skills, preferred_skills = _extract_skills(jd_text)
    hidden_reqs = _infer_hidden_requirements(required_skills, preferred_skills)
    locations = _extract_locations(jd_text)
    negative_signals = _extract_negative_signals(jd_text)

    return ParsedJD(
        role=role,
        seniority=seniority,
        seniority_level=seniority_level,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        negative_signals=negative_signals,
        experience_min=exp_min,
        experience_max=exp_max,
        hidden_requirements=hidden_reqs,
        industry_keywords=["AI", "ML", "NLP", "Retrieval", "Ranking"],
        location_preferences=locations,
        jd_text=jd_text,
    )


# ===========================================================================
# Standalone test
# ===========================================================================
if __name__ == "__main__":
    import json
    from src.config import JD_TEXT

    parsed = parse_jd(JD_TEXT)
    print(json.dumps(parsed.to_dict(), indent=2))
