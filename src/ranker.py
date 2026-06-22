"""
ranker.py — Multi-Dimensional Ranking Engine

Phase 3 deliverable. The BRAIN of the system.

# ═══════════════════════════════════════════════════════════════════════════
# NOTE FOR VIVEK:
#
# This file is Seema's REFERENCE scorer. It computes 5 scoring dimensions
# using the JD intelligence + skill taxonomy that Seema built.
#
# You can:
#   1. ADD new scoring functions here (hidden_talent_score, authenticity_score)
#   2. MODIFY existing functions (e.g., improve compute_skill_score)
#   3. ADJUST the rank_candidate() function to include your new dimensions
#   4. UPDATE compute_final_score() if you add new weight dimensions
#
# The scoring formula weights live in src/config.py → WEIGHTS dict.
# Currently: semantic=0.30, skill=0.30, experience=0.15, career=0.15, behavior=0.10
#
# Your additions should NOT break the existing function signatures — the
# pipeline in rank.py calls rank_candidate(candidate, parsed_jd, semantic_score).
# ═══════════════════════════════════════════════════════════════════════════

Computes 5 scoring dimensions for each candidate:
  1. Semantic Score  (0-100) — Embedding cosine similarity
  2. Skill Score     (0-100) — Hard skill match with proficiency/endorsement weighting
  3. Experience Score(0-100) — Years-of-experience fit with asymmetric penalties
  4. Career Score    (0-100) — Title progression + industry + company type + stability
  5. Behavior Score  (0-100) — Redrob platform signals (availability, engagement)

Final formula:
  final_score = (0.30 * semantic + 0.30 * skill + 0.15 * experience
                 + 0.15 * career + 0.10 * behavior)

Key design decisions (inspired by the JD's explicit hints):
  - Title relevance is weighted heavily: a "Marketing Manager" with all AI keywords
    is a TRAP (the JD says so explicitly)
  - Pure services background is penalized (JD says: "only worked at TCS/Infosys/Wipro")
  - Behavioral signals matter: inactive candidates are down-weighted
  - Hidden requirements give bonus: "Production AI" implies Docker/K8s knowledge
"""

from dataclasses import dataclass, field
from datetime import datetime, date

from src.jd_parser import ParsedJD
from src.utils.skills import (
    normalize_skill,
    get_proficiency_weight,
    is_ai_relevant,
    is_non_tech,
    get_skill_domain,
)
from src.utils.mappings import (
    get_title_seniority,
    find_cluster_match,
    get_industry_relevance,
    is_services_company,
    SERVICES_COMPANIES,
)
from src.config import (
    WEIGHTS,
    SKILL_CONFIG,
    EXPERIENCE_CONFIG,
    CAREER_CONFIG,
    BEHAVIOR_CONFIG,
)


@dataclass
class CandidateScore:
    """Detailed scoring breakdown for a single candidate."""
    candidate_id: str
    semantic_score: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    career_score: float = 0.0
    behavior_score: float = 0.0
    final_score: float = 0.0
    reasoning: str = ""

    # Detailed breakdowns for debugging / transparency
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    title_relevance: str = ""
    flags: list[str] = field(default_factory=list)


# ===========================================================================
# Skill Scoring
# ===========================================================================
def compute_skill_score(candidate: dict, parsed_jd: ParsedJD) -> tuple[float, list[str], list[str]]:
    """Compute skill match score between candidate and JD.

    Returns:
        (score 0-100, matched_skills list, missing_skills list)
    """
    candidate_skills = candidate.get("skills", [])
    if not candidate_skills:
        return 0.0, [], list(parsed_jd.required_skills)

    # Build candidate skill profile: canonical_name → {proficiency, endorsements, duration}
    cand_skill_map = {}
    for skill_entry in candidate_skills:
        canonical = normalize_skill(skill_entry["name"])
        prof_weight = get_proficiency_weight(skill_entry.get("proficiency", "beginner"))
        endorsements = skill_entry.get("endorsements", 0)
        duration = skill_entry.get("duration_months", 0)

        # Endorsement boost
        endorsement_boost = min(
            SKILL_CONFIG["endorsement_cap"],
            SKILL_CONFIG["endorsement_base"] + endorsements * SKILL_CONFIG["endorsement_multiplier"]
        )

        # Duration trust
        duration_trust = max(
            SKILL_CONFIG["duration_trust_floor"],
            min(1.0, duration / SKILL_CONFIG["duration_trust_threshold_months"])
        )

        # Combined skill weight
        weight = prof_weight * endorsement_boost * duration_trust
        cand_skill_map[canonical] = max(cand_skill_map.get(canonical, 0), weight)

    # Match against required skills
    required = parsed_jd.required_skills
    matched = []
    missing = []
    total_weight = 0.0

    for req_skill in required:
        req_canonical = normalize_skill(req_skill)

        # Exact match
        if req_canonical in cand_skill_map:
            total_weight += cand_skill_map[req_canonical]
            matched.append(req_skill)
            continue

        # Cluster match: check if candidate has a related skill
        best_cluster_match = 0.0
        best_cluster_skill = None
        for cand_skill, cand_weight in cand_skill_map.items():
            cluster_sim = find_cluster_match(req_canonical, cand_skill)
            if cluster_sim > 0 and cluster_sim * cand_weight > best_cluster_match:
                best_cluster_match = cluster_sim * cand_weight
                best_cluster_skill = cand_skill

        if best_cluster_skill:
            total_weight += best_cluster_match
            matched.append(f"{req_skill}~{best_cluster_skill}")
        else:
            missing.append(req_skill)

    # Base score: fraction of required skills matched (weighted)
    if required:
        base_score = (total_weight / len(required)) * 100
    else:
        base_score = 50.0  # No requirements = neutral

    # Preferred skills bonus
    preferred_bonus = 0.0
    for pref_skill in parsed_jd.preferred_skills:
        pref_canonical = normalize_skill(pref_skill)
        if pref_canonical in cand_skill_map:
            preferred_bonus += 3.0  # Small bonus per preferred skill
        else:
            for cand_skill in cand_skill_map:
                if find_cluster_match(pref_canonical, cand_skill) > 0:
                    preferred_bonus += 1.5
                    break

    # Hidden requirements bonus
    hidden_bonus = 0.0
    for hidden in parsed_jd.hidden_requirements:
        hidden_canonical = normalize_skill(hidden)
        if hidden_canonical in cand_skill_map:
            hidden_bonus += SKILL_CONFIG["hidden_requirement_bonus"]

    # Non-tech ratio penalty (catches keyword-stuffing trap candidates)
    total_skills = len(cand_skill_map)
    non_tech_count = sum(1 for s in cand_skill_map if is_non_tech(s))
    if total_skills > 0:
        non_tech_ratio = non_tech_count / total_skills
        if non_tech_ratio > SKILL_CONFIG["non_tech_ratio_penalty_threshold"]:
            base_score *= SKILL_CONFIG["non_tech_ratio_penalty"]

    final_score = min(100.0, base_score + preferred_bonus + hidden_bonus)
    return max(0.0, final_score), matched, missing


# ===========================================================================
# Experience Scoring
# ===========================================================================
def compute_experience_score(candidate: dict, parsed_jd: ParsedJD) -> float:
    """Compute experience-fit score.

    Asymmetric penalty:
      - Under-experienced: sharp falloff (15 pts per year below)
      - Over-experienced: gentle falloff (5 pts per year above threshold)
    """
    cand_years = candidate.get("profile", {}).get("years_of_experience", 0)
    req_min = parsed_jd.experience_min
    req_max = parsed_jd.experience_max
    tolerance = EXPERIENCE_CONFIG["perfect_match_tolerance"]

    # Perfect match zone
    if (req_min - tolerance) <= cand_years <= (req_max + tolerance):
        return 100.0

    # Under-experienced
    if cand_years < req_min - tolerance:
        gap = (req_min - tolerance) - cand_years
        penalty = gap * EXPERIENCE_CONFIG["under_penalty_per_year"]
        return max(0.0, 100.0 - penalty)

    # Over-experienced
    if cand_years > req_max + tolerance:
        excess = cand_years - (req_max + tolerance)
        over_threshold = EXPERIENCE_CONFIG["over_threshold"]
        if excess <= over_threshold:
            return 100.0  # Slight over is fine
        penalty = (excess - over_threshold) * EXPERIENCE_CONFIG["over_penalty_per_year"]
        return max(EXPERIENCE_CONFIG["over_floor"], 100.0 - penalty)

    return 100.0


# ===========================================================================
# Career Scoring
# ===========================================================================
def compute_career_score(candidate: dict, parsed_jd: ParsedJD) -> tuple[float, str, list[str]]:
    """Compute career trajectory score.

    Components:
      - Title progression: ascending seniority = good
      - Industry relevance: tech/AI industries = bonus
      - Company type: product companies > services
      - Stability: reasonable tenure per role

    Returns:
        (score 0-100, title_relevance label, flags list)
    """
    career = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    flags = []

    if not career:
        return 30.0, "unknown", ["no_career_history"]

    # ---- 1. Title Progression ----
    seniority_levels = []
    for job in career:
        title = job.get("title", "")
        level = get_title_seniority(title)
        seniority_levels.append(level)

    # Career should go from lower to higher (earliest job to latest)
    # career_history is typically most-recent-first, so reverse
    progression_score = 50.0  # Default neutral
    if len(seniority_levels) >= 2:
        levels_chronological = list(reversed(seniority_levels))
        increases = sum(1 for i in range(len(levels_chronological) - 1)
                       if levels_chronological[i + 1] > levels_chronological[i])
        decreases = sum(1 for i in range(len(levels_chronological) - 1)
                       if levels_chronological[i + 1] < levels_chronological[i])
        stagnant = sum(1 for i in range(len(levels_chronological) - 1)
                      if levels_chronological[i + 1] == levels_chronological[i])

        total_transitions = len(levels_chronological) - 1
        if total_transitions > 0:
            progression_score = ((increases * 100 + stagnant * 50) / total_transitions)
            if decreases > 0:
                flags.append("career_regression")
                progression_score *= 0.7

    # ---- 2. Title Relevance to AI/ML ----
    current_title = profile.get("current_title", "").lower()
    title_relevance = "neutral"

    ai_keywords = CAREER_CONFIG["ai_title_keywords"]
    non_ai_keywords = CAREER_CONFIG["non_ai_title_keywords"]

    is_ai_title = any(kw in current_title for kw in ai_keywords)
    is_non_ai_title = any(kw in current_title for kw in non_ai_keywords)

    if is_ai_title and not is_non_ai_title:
        title_relevance = "strong_match"
        title_bonus = 30
    elif is_non_ai_title and not is_ai_title:
        title_relevance = "weak_match"
        title_bonus = -20
        flags.append("non_ai_title")
    else:
        title_bonus = 0

    # ---- 3. Industry Relevance ----
    industries = [job.get("industry", "") for job in career]
    industry_scores = [get_industry_relevance(ind) for ind in industries if ind]
    avg_industry = sum(industry_scores) / max(1, len(industry_scores))
    industry_score = avg_industry * 100

    # ---- 4. Company Type (Product vs Services) ----
    companies = [job.get("company", "") for job in career]
    services_count = sum(1 for c in companies if is_services_company(c))
    total_companies = max(1, len(companies))

    if services_count == total_companies and total_companies > 1:
        # ALL career at services companies — JD explicitly warns against this
        company_score = 20.0
        flags.append("all_services_career")
    elif services_count > 0:
        # Mixed: some services, some product
        company_score = 100 - (services_count / total_companies * 60)
    else:
        company_score = 100.0

    # ---- 5. Stability ----
    durations = [job.get("duration_months", 0) for job in career]
    avg_tenure = sum(durations) / max(1, len(durations))
    min_tenure = CAREER_CONFIG["min_avg_tenure_months"]

    if avg_tenure >= min_tenure:
        stability_score = 100.0
    else:
        # Job hopping penalty
        stability_score = max(20.0, (avg_tenure / min_tenure) * 100)
        if avg_tenure < 12:
            flags.append("job_hopper")

    # ---- Combine ----
    career_score = (
        progression_score * CAREER_CONFIG["progression_weight"]
        + industry_score * CAREER_CONFIG["industry_weight"]
        + company_score * CAREER_CONFIG["company_type_weight"]
        + stability_score * CAREER_CONFIG["stability_weight"]
        + title_bonus
    )

    # All-services penalty (multiplicative)
    if "all_services_career" in flags:
        career_score *= CAREER_CONFIG["all_services_penalty"]

    return max(0.0, min(100.0, career_score)), title_relevance, flags


# ===========================================================================
# Behavior Scoring
# ===========================================================================
def compute_behavior_score(candidate: dict) -> float:
    """Compute behavioral engagement score from Redrob signals.

    From the JD:
      "A perfect-on-paper candidate who hasn't logged in for 6 months and
       has a 5% recruiter response rate is, for hiring purposes, not actually
       available. Down-weight them appropriately."
    """
    signals = candidate.get("redrob_signals", {})
    if not signals:
        return 30.0  # No signals = low confidence

    cfg = BEHAVIOR_CONFIG

    # 1. Profile completeness (0-100 already)
    completeness = signals.get("profile_completeness_score", 50)

    # 2. Recruiter response rate (0-1 → 0-100)
    response_rate = signals.get("recruiter_response_rate", 0) * 100

    # 3. Response time (lower is better)
    avg_response_hours = signals.get("avg_response_time_hours", 168)
    max_hours = cfg["response_time_max_hours"]
    response_time_score = max(0, 100 - (avg_response_hours / max_hours * 100))

    # 4. GitHub activity (-1 = no account, 0-100 otherwise)
    github = signals.get("github_activity_score", -1)
    if github < 0:
        github_score = 30.0  # Neutral — don't penalize for no GitHub
    else:
        github_score = github

    # 5. Interview completion rate (0-1 → 0-100)
    interview_rate = signals.get("interview_completion_rate", 0.5) * 100

    # 6. Verification bonus
    verified_email = signals.get("verified_email", False)
    verified_phone = signals.get("verified_phone", False)
    linkedin = signals.get("linkedin_connected", False)
    verification_score = (
        (40 if verified_email else 0)
        + (30 if verified_phone else 0)
        + (30 if linkedin else 0)
    )

    # 7. Recency (days since last active)
    last_active_str = signals.get("last_active_date", "")
    recency_score = 50.0  # default
    if last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
            today = date(2026, 6, 15)  # Approximate challenge date
            days_inactive = (today - last_active).days
            max_days = cfg["recency_max_days"]
            if days_inactive <= 0:
                recency_score = 100.0
            elif days_inactive >= max_days:
                recency_score = 0.0
            else:
                recency_score = max(0, 100 - (days_inactive / max_days * 100))
        except (ValueError, TypeError):
            recency_score = 50.0

    # Weighted combination
    behavior = (
        completeness * cfg["profile_completeness_weight"]
        + response_rate * cfg["response_rate_weight"]
        + response_time_score * cfg["response_time_weight"]
        + github_score * cfg["github_weight"]
        + interview_rate * cfg["interview_rate_weight"]
        + verification_score * cfg["verification_weight"]
        + recency_score * cfg["recency_weight"]
    )

    # Open-to-work bonus
    if signals.get("open_to_work_flag", False):
        behavior *= cfg["open_to_work_bonus"]

    return max(0.0, min(100.0, behavior))


# ===========================================================================
# Final Score Composition + Reasoning
# ===========================================================================
def compute_final_score(scores: CandidateScore) -> float:
    """Combine all dimension scores into a final score using configured weights."""
    final = (
        scores.semantic_score * WEIGHTS["semantic"]
        + scores.skill_score * WEIGHTS["skill"]
        + scores.experience_score * WEIGHTS["experience"]
        + scores.career_score * WEIGHTS["career"]
        + scores.behavior_score * WEIGHTS["behavior"]
    )
    return round(final / 100, 4)  # Normalize to 0-1 range


def generate_reasoning(candidate: dict, scores: CandidateScore) -> str:
    """Generate a concise one-line reasoning string for the ranking.

    Format matches submission sample:
      "ML Engineer with 6.4 yrs; skill match 85%; semantic 92%; career growth strong"
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "Unknown")
    years = profile.get("years_of_experience", 0)

    parts = [
        f"{title} with {years} yrs",
        f"skill:{scores.skill_score:.0f}%",
        f"semantic:{scores.semantic_score:.0f}%",
        f"exp:{scores.experience_score:.0f}%",
        f"career:{scores.career_score:.0f}%",
    ]

    # Add response rate from signals
    signals = candidate.get("redrob_signals", {})
    rr = signals.get("recruiter_response_rate", 0)
    parts.append(f"response rate {rr:.2f}")

    # Add flags if any
    if scores.flags:
        parts.append(f"flags:{','.join(scores.flags[:2])}")

    return "; ".join(parts)


# ===========================================================================
# Full ranking pipeline for a single candidate
# ===========================================================================
def rank_candidate(candidate: dict, parsed_jd: ParsedJD,
                   semantic_score: float = 50.0) -> CandidateScore:
    """Score a candidate across all dimensions.

    Args:
        candidate: Raw candidate dict from JSON/JSONL
        parsed_jd: Parsed job description
        semantic_score: Pre-computed semantic similarity score (0-100)

    Returns:
        CandidateScore with all dimensions filled
    """
    cid = candidate.get("candidate_id", "UNKNOWN")

    # Skill score
    skill_score, matched, missing = compute_skill_score(candidate, parsed_jd)

    # Experience score
    exp_score = compute_experience_score(candidate, parsed_jd)

    # Career score
    career_score, title_rel, flags = compute_career_score(candidate, parsed_jd)

    # Behavior score
    behavior_score = compute_behavior_score(candidate)

    # Build result
    result = CandidateScore(
        candidate_id=cid,
        semantic_score=semantic_score,
        skill_score=skill_score,
        experience_score=exp_score,
        career_score=career_score,
        behavior_score=behavior_score,
        matched_skills=matched,
        missing_skills=missing,
        title_relevance=title_rel,
        flags=flags,
    )

    # Final score
    result.final_score = compute_final_score(result)

    # Reasoning
    result.reasoning = generate_reasoning(candidate, result)

    return result


# ===========================================================================
# Standalone test
# ===========================================================================
if __name__ == "__main__":
    import json
    from src.config import JD_TEXT
    from src.jd_parser import parse_jd

    parsed = parse_jd(JD_TEXT)
    print("Parsed JD:")
    print(json.dumps(parsed.to_dict(), indent=2))
    print()

    # Create a mock candidate
    mock_candidate = {
        "candidate_id": "CAND_TEST001",
        "profile": {
            "anonymized_name": "Test User",
            "headline": "Senior ML Engineer | Python, PyTorch, FAISS",
            "summary": "6 years building ranking and retrieval systems at product companies.",
            "location": "Pune, Maharashtra",
            "country": "India",
            "years_of_experience": 6.5,
            "current_title": "Senior ML Engineer",
            "current_company": "Startup Inc",
            "current_company_size": "51-200",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "company": "Startup Inc",
                "title": "Senior ML Engineer",
                "start_date": "2022-01-01",
                "end_date": None,
                "duration_months": 30,
                "is_current": True,
                "industry": "Software",
                "company_size": "51-200",
                "description": "Built end-to-end ranking system using sentence-transformers and FAISS.",
            },
            {
                "company": "BigCo",
                "title": "ML Engineer",
                "start_date": "2019-06-01",
                "end_date": "2021-12-31",
                "duration_months": 31,
                "is_current": False,
                "industry": "Technology",
                "company_size": "1001-5000",
                "description": "Worked on recommendation engine using embeddings and vector search.",
            },
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 30, "duration_months": 60},
            {"name": "PyTorch", "proficiency": "advanced", "endorsements": 15, "duration_months": 36},
            {"name": "FAISS", "proficiency": "advanced", "endorsements": 10, "duration_months": 24},
            {"name": "sentence-transformers", "proficiency": "advanced", "endorsements": 8, "duration_months": 18},
            {"name": "Docker", "proficiency": "intermediate", "endorsements": 5, "duration_months": 30},
            {"name": "Kubernetes", "proficiency": "intermediate", "endorsements": 3, "duration_months": 12},
        ],
        "education": [
            {
                "institution": "IIT Delhi",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "start_year": 2013,
                "end_year": 2017,
                "grade": "8.5 CGPA",
                "tier": "tier_1",
            }
        ],
        "certifications": [],
        "languages": [{"language": "English", "proficiency": "professional"}],
        "redrob_signals": {
            "profile_completeness_score": 92.0,
            "signup_date": "2025-01-15",
            "last_active_date": "2026-06-10",
            "open_to_work_flag": True,
            "profile_views_received_30d": 45,
            "applications_submitted_30d": 3,
            "recruiter_response_rate": 0.85,
            "avg_response_time_hours": 12.5,
            "skill_assessment_scores": {"Python": 88, "PyTorch": 75},
            "connection_count": 500,
            "endorsements_received": 80,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 25, "max": 40},
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": True,
            "github_activity_score": 72,
            "search_appearance_30d": 150,
            "saved_by_recruiters_30d": 12,
            "interview_completion_rate": 0.92,
            "offer_acceptance_rate": 0.75,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
        },
    }

    result = rank_candidate(mock_candidate, parsed, semantic_score=88.5)
    print(f"Candidate: {result.candidate_id}")
    print(f"  Skill Score:      {result.skill_score:.1f}")
    print(f"  Semantic Score:    {result.semantic_score:.1f}")
    print(f"  Experience Score:  {result.experience_score:.1f}")
    print(f"  Career Score:      {result.career_score:.1f}")
    print(f"  Behavior Score:    {result.behavior_score:.1f}")
    print(f"  FINAL SCORE:       {result.final_score:.4f}")
    print(f"  Reasoning:         {result.reasoning}")
    print(f"  Matched Skills:    {result.matched_skills}")
    print(f"  Missing Skills:    {result.missing_skills}")
    print(f"  Flags:             {result.flags}")
