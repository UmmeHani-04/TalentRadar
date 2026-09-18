"""
vivek_module.py — RecruiterGPT Advanced Scoring Models

Contains the new Core Modules for the Explainable Talent Discovery Engine:
- Core Module 3: Hidden Talent Discovery
- Core Module 4: Skill Authenticity Detector
- Core Module 5: Career Momentum Analysis
- Core Module 6: Future Potential Score
"""

from src.config import AUTHENTICITY_CONFIG, MOMENTUM_CONFIG, POTENTIAL_CONFIG
from src.utils.mappings import get_title_seniority
from src.utils.skills import normalize_skill
from src.jd_parser import ParsedJD

def compute_authenticity_score(candidate: dict) -> float:
    """Core Module 4: Skill Authenticity Detector.
    
    Verifies whether career history and projects support claimed skills.
    Penalizes skills with low duration and zero endorsements.
    """
    skills = candidate.get("skills", [])
    if not skills:
        return 50.0

    score = AUTHENTICITY_CONFIG["base_authenticity"]
    unverified_penalty = AUTHENTICITY_CONFIG["unverified_skill_penalty"]
    
    for skill in skills:
        duration = skill.get("duration_months", 0)
        endorsements = skill.get("endorsements", 0)
        
        # A skill claimed for < 6 months with 0 endorsements is considered unverified
        if duration < 6 and endorsements == 0:
            score -= unverified_penalty
            
    return max(0.0, float(score))

def compute_momentum_score(candidate: dict) -> float:
    """Core Module 5: Career Momentum Analysis.
    
    Tracks promotion speed and title progression.
    Candidate B (Intern -> Engineer -> Lead) > Candidate A (Engineer x4).
    """
    career = candidate.get("career_history", [])
    if not career:
        return 30.0

    seniority_levels = []
    for job in career:
        level = get_title_seniority(job.get("title", ""))
        seniority_levels.append(level)
        
    score = 50.0 # Neutral start
    
    if len(seniority_levels) >= 2:
        levels_chrono = list(reversed(seniority_levels))
        durations = list(reversed([job.get("duration_months", 0) for job in career]))
        
        increases = 0
        stagnant = 0
        decreases = 0
        
        for i in range(len(levels_chrono) - 1):
            if levels_chrono[i+1] > levels_chrono[i]:
                increases += 1
                # Bonus if promoted within 18 months
                if durations[i] <= 18:
                    score += MOMENTUM_CONFIG["fast_promotion_bonus"]
            elif levels_chrono[i+1] < levels_chrono[i]:
                decreases += 1
            else:
                stagnant += 1
                
        # Stagnation penalty
        for dur in durations:
            if dur > 48: # > 4 years in same role
                score -= MOMENTUM_CONFIG["stagnation_penalty"]
                
        total_transitions = max(1, len(levels_chrono) - 1)
        base_progression = (increases * 40 + stagnant * 10 - decreases * 20)
        score += base_progression
        
    return max(0.0, min(100.0, float(score)))

def compute_potential_score(candidate: dict) -> float:
    """Core Module 6: Future Potential Score.
    
    Predicts future value based on learning speed (recent certs) 
    and diverse tech stacks.
    """
    score = float(POTENTIAL_CONFIG["base_potential"])
    
    # Check certifications
    certs = candidate.get("certifications", [])
    # In a real system, we'd check dates. Here we assume presence = recent learning.
    if certs:
        score += POTENTIAL_CONFIG["recent_cert_bonus"] * len(certs)
        
    # Check diverse tech stacks (e.g., frontend + backend + cloud)
    skills = candidate.get("skills", [])
    skill_names = [s.get("name", "").lower() for s in skills]
    
    has_frontend = any(s in skill_names for s in ["react", "vue", "angular", "javascript", "typescript"])
    has_backend = any(s in skill_names for s in ["python", "java", "go", "node.js", "rust"])
    has_cloud = any(s in skill_names for s in ["aws", "gcp", "azure", "docker", "kubernetes"])
    has_ai = any(s in skill_names for s in ["machine learning", "pytorch", "tensorflow", "llm", "nlp"])
    
    stack_count = sum([has_frontend, has_backend, has_cloud, has_ai])
    if stack_count >= 3:
        score += POTENTIAL_CONFIG["diverse_stack_bonus"]
        
    return max(0.0, min(100.0, score))

def compute_hidden_talent_score(candidate: dict, parsed_jd: ParsedJD) -> float:
    """Core Module 3: Hidden Talent Discovery.
    
    Finds candidates who lack exact keywords but possess transferable skills
    implied by the JD's hidden requirements.
    """
    score = 30.0 # Baseline
    
    hidden_reqs = set([normalize_skill(s) for s in parsed_jd.hidden_requirements])
    if not hidden_reqs:
        return 50.0 # If no hidden reqs, neutral score
        
    candidate_skills = set([normalize_skill(s.get("name", "")) for s in candidate.get("skills", [])])
    
    # Check overlap
    overlap = hidden_reqs.intersection(candidate_skills)
    
    if overlap:
        # Score is proportional to how many hidden requirements they actually meet
        match_ratio = len(overlap) / len(hidden_reqs)
        score = 50.0 + (50.0 * match_ratio)
        
    return max(0.0, min(100.0, score))
