"""
config.py — Centralized weights, thresholds, and hyperparameters.

All tunable parameters live here so you can adjust scoring behavior
without touching any logic code. Each weight is documented with its rationale.
"""

# ---------------------------------------------------------------------------
# Final score composition weights (must sum to 1.0)
# ---------------------------------------------------------------------------
# The JD emphasizes: skills > semantic > experience > career > behavior
WEIGHTS = {
    "semantic":    0.30,   # Embedding-based JD ↔ candidate similarity
    "skill":       0.30,   # Hard skill match (exact + cluster)
    "experience":  0.15,   # Years of experience match
    "career":      0.15,   # Career trajectory + industry + company type
    "behavior":    0.10,   # Redrob platform signals (availability, engagement)
}

# ---------------------------------------------------------------------------
# Skill scoring parameters
# ---------------------------------------------------------------------------
SKILL_CONFIG = {
    # How much credit for cluster-match vs exact-match
    "cluster_match_weight": 0.70,

    # Endorsement boost: min(1.0, base + endorsements * multiplier)
    "endorsement_base": 0.80,
    "endorsement_multiplier": 0.01,
    "endorsement_cap": 1.0,

    # Duration trust: min(1.0, duration_months / threshold)
    # Skills used < 6 months get heavily discounted
    "duration_trust_threshold_months": 24,
    "duration_trust_floor": 0.3,

    # Bonus points per matched hidden requirement (added to raw skill score)
    "hidden_requirement_bonus": 3.0,

    # Penalty for having mostly non-tech skills (suggests non-technical profile)
    "non_tech_ratio_penalty_threshold": 0.6,  # If >60% skills are non-tech
    "non_tech_ratio_penalty": 0.5,            # Multiply skill score by 0.5
}

# ---------------------------------------------------------------------------
# Experience scoring parameters
# ---------------------------------------------------------------------------
EXPERIENCE_CONFIG = {
    # How far from ideal before penalty kicks in
    "perfect_match_tolerance": 1.0,   # ±1 year = full score

    # Under-experienced penalty: per year below requirement
    "under_penalty_per_year": 15,

    # Over-experienced penalty: per year above (requirement + 4)
    "over_threshold": 4,              # Start penalizing at +4 years over
    "over_penalty_per_year": 5,
    "over_floor": 60,                 # Never go below 60 for over-experience
}

# ---------------------------------------------------------------------------
# Career scoring parameters
# ---------------------------------------------------------------------------
CAREER_CONFIG = {
    # Career progression
    "progression_weight": 0.35,       # Weight for title progression score
    "industry_weight": 0.25,          # Weight for industry relevance
    "company_type_weight": 0.25,      # Weight for product vs services companies
    "stability_weight": 0.15,         # Weight for job tenure/stability

    # Job-hopping penalty: avg tenure below this gets penalized
    "min_avg_tenure_months": 18,

    # Pure services penalty (from JD: "People who have only worked at
    # consulting firms in their entire career")
    "all_services_penalty": 0.4,      # Multiply career score by 0.4

    # Title relevance: AI/ML/Data titles vs non-tech titles
    "ai_title_keywords": [
        "ai", "ml", "machine learning", "data scientist", "data engineer",
        "research", "nlp", "deep learning", "backend engineer",
        "software engineer", "developer", "engineer",
    ],
    "non_ai_title_keywords": [
        "marketing", "hr", "sales", "accountant", "content writer",
        "graphic designer", "customer support", "operations",
        "civil engineer", "mechanical engineer",
    ],
}

# ---------------------------------------------------------------------------
# Behavior scoring parameters
# ---------------------------------------------------------------------------
BEHAVIOR_CONFIG = {
    # Component weights within behavior score (sum to 1.0)
    "profile_completeness_weight":  0.15,
    "response_rate_weight":         0.25,
    "response_time_weight":         0.10,
    "github_weight":                0.15,
    "interview_rate_weight":        0.10,
    "verification_weight":          0.10,
    "recency_weight":               0.15,

    # Response time scoring: max hours for full score
    "response_time_max_hours": 72,

    # Recency: days since last active → score
    "recency_max_days": 180,         # Inactive >180 days = 0 recency score

    # Open to work bonus (multiplier on behavior score)
    "open_to_work_bonus": 1.15,
}

# ---------------------------------------------------------------------------
# Semantic matcher parameters
# ---------------------------------------------------------------------------
SEMANTIC_CONFIG = {
    "model_name": "all-MiniLM-L6-v2",
    "batch_size": 256,
    "prefilter_top_n": 5000,         # Only compute embeddings for top N from rule-based
}

# ---------------------------------------------------------------------------
# Pipeline parameters
# ---------------------------------------------------------------------------
PIPELINE_CONFIG = {
    "top_k": 100,                    # Final output: top 100 candidates
    "candidates_file": "candidates.jsonl",
    "output_file": "submission.csv",
}

# ---------------------------------------------------------------------------
# The actual Job Description text (from job_description.docx)
# ---------------------------------------------------------------------------
JD_TEXT = """
Job Description: Senior AI Engineer — Founding Team

Company: Redrob AI (Series A AI-native talent intelligence platform)
Location: Pune/Noida, India (Hybrid — flexible cadence) | Open to relocation candidates from Tier-1 Indian cities
Employment Type: Full-time
Experience Required: 5–9 years

Role: Own the intelligence layer of Redrob's product — the ranking, retrieval, and matching systems that decide what recruiters see when they search for candidates and what candidates see when they search for roles.

First 90 days:
- Audit current BM25 + rule-based scoring system
- Ship a v2 ranking system with embeddings, hybrid retrieval, and LLM-based re-ranking
- Set up evaluation infrastructure — offline benchmarks, online A/B testing, recruiter-feedback loops

Things you absolutely need:
- Production experience with embeddings-based retrieval systems (sentence-transformers, OpenAI embeddings, BGE, E5)
- Production experience with vector databases or hybrid search (Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS)
- Strong Python with high code quality
- Hands-on experience designing evaluation frameworks for ranking systems (NDCG, MRR, MAP, A/B testing)

Things we'd like you to have:
- LLM fine-tuning experience (LoRA, QLoRA, PEFT)
- Experience with learning-to-rank models (XGBoost-based or neural)
- Prior exposure to HR-tech, recruiting tech, or marketplace products
- Background in distributed systems or large-scale inference optimization
- Open-source contributions in the AI/ML space

Things we explicitly do NOT want:
- Title-chasers switching companies every 1.5 years for promotions
- Framework enthusiasts without systems thinking
- People who have ONLY worked at consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini) their entire career
- People whose primary expertise is computer vision, speech, or robotics without NLP/IR exposure
- People whose work has been entirely on closed-source proprietary systems for 5+ years

Ideal candidate profile:
- 6-8 years total experience, 4-5 in applied ML/AI at product companies
- Shipped at least one end-to-end ranking, search, or recommendation system
- Strong opinions about retrieval, evaluation, and LLM integration
- Located in or willing to relocate to Noida or Pune
- Active on Redrob platform

Notice period: Prefer sub-30-day. 30+ days candidates face a higher bar.
"""
