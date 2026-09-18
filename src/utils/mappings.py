"""
mappings.py — Hidden requirements, semantic skill clusters, title seniority ladder.

This is where the "recruiter intuition" lives. The JD says "Production AI Deployment"
but what it MEANS is Docker + Kubernetes + CI/CD + Monitoring. This module encodes
that implicit knowledge.

Key insight from the JD:
  "The right answer involves reasoning about the gap between what the JD says
   and what the JD means."
"""

# ---------------------------------------------------------------------------
# Hidden requirements: JD phrase → implied skills
# When a JD mentions a high-level concept, these are the skills a real
# recruiter would expect the candidate to have.
# ---------------------------------------------------------------------------
HIDDEN_REQUIREMENTS_MAP = {
    # Production deployment implies ops knowledge
    "production ai deployment": [
        "docker", "kubernetes", "ci/cd", "monitoring", "aws", "gcp", "azure",
    ],
    "production deployment": [
        "docker", "kubernetes", "ci/cd", "monitoring",
    ],
    "production ml": [
        "docker", "kubernetes", "ci/cd", "monitoring", "mlflow",
    ],

    # LLM work implies transformer ecosystem
    "large language models": [
        "transformers", "pytorch", "hugging face", "python",
    ],
    "llm fine-tuning": [
        "pytorch", "hugging face", "transformers", "wandb",
    ],

    # Retrieval/search implies vector DB + embeddings
    "information retrieval": [
        "vector databases", "elasticsearch", "sentence transformers",
        "python", "ranking",
    ],
    "retrieval augmented generation": [
        "vector databases", "large language models", "sentence transformers",
        "python",
    ],
    "ranking": [
        "python", "machine learning", "information retrieval",
    ],

    # Vector DB implies embeddings knowledge
    "vector databases": [
        "sentence transformers", "machine learning", "python",
    ],

    # Embeddings implies ML foundations
    "sentence transformers": [
        "python", "pytorch", "natural language processing",
    ],

    # Cloud implies ops
    "aws": ["docker", "ci/cd"],
    "gcp": ["docker", "ci/cd"],
    "azure": ["docker", "ci/cd"],

    # Data engineering implies pipeline knowledge
    "data engineering": [
        "sql", "python", "airflow",
    ],
}

# ---------------------------------------------------------------------------
# Semantic skill clusters: skills that are "close enough" to match each other.
# If JD requires "vector databases", a candidate with "FAISS" gets partial credit.
# Similarity within a cluster is 0.75 (vs 1.0 for exact match).
# ---------------------------------------------------------------------------
SEMANTIC_SKILL_CLUSTERS = {
    "vector_stores": {
        "vector databases", "faiss", "pinecone", "qdrant", "weaviate",
        "milvus", "chromadb",
    },
    "search_engines": {
        "elasticsearch", "opensearch", "information retrieval",
    },
    "embeddings": {
        "sentence transformers", "hugging face", "transformers",
    },
    "llm_ecosystem": {
        "large language models", "llm fine-tuning", "langchain",
        "llamaindex", "retrieval augmented generation",
    },
    "ml_frameworks": {
        "tensorflow", "pytorch", "keras",
    },
    "boosting": {
        "xgboost", "lightgbm", "catboost",
    },
    "cloud_providers": {
        "aws", "gcp", "azure",
    },
    "container_orchestration": {
        "docker", "kubernetes",
    },
    "data_processing": {
        "spark", "beam", "flink",
    },
    "data_orchestration": {
        "airflow", "data engineering",
    },
    "nlp_ir": {
        "natural language processing", "information retrieval",
        "ranking", "recommendation systems",
    },
    "cv_skills": {
        "computer vision", "image classification", "object detection", "gans",
    },
}

# Cluster match weight (vs 1.0 for exact match)
CLUSTER_MATCH_WEIGHT = 0.70

# ---------------------------------------------------------------------------
# Title seniority ladder: maps job titles to a numeric seniority level.
# Used for career progression scoring.
# Higher number = more senior.
# ---------------------------------------------------------------------------
TITLE_SENIORITY = {
    # Internship / Entry
    "intern":                           1,
    "trainee":                          1,
    "apprentice":                       1,
    "fresher":                          1,

    # Junior
    "junior developer":                 2,
    "junior engineer":                  2,
    "junior software engineer":         2,
    "junior data scientist":            2,
    "junior ml engineer":               2,
    "associate engineer":               2,
    "associate developer":              2,
    "analyst":                          2,
    "business analyst":                 2,
    "customer support":                 2,

    # Mid-level
    "software engineer":                3,
    "developer":                        3,
    "engineer":                         3,
    "data scientist":                   3,
    "data engineer":                    3,
    "data analyst":                     3,
    "ml engineer":                      3,
    "ai engineer":                      3,
    "backend engineer":                 3,
    "frontend engineer":                3,
    "full stack engineer":              3,
    "devops engineer":                  3,
    "cloud engineer":                   3,
    "research engineer":                3,
    "content writer":                   3,
    "accountant":                       3,
    "graphic designer":                 3,
    "marketing manager":                3,
    "hr manager":                       3,
    "operations manager":               3,
    "sales executive":                  3,
    "project manager":                  3,
    "mechanical engineer":              3,
    "civil engineer":                   3,

    # Senior
    "senior software engineer":         4,
    "senior developer":                 4,
    "senior engineer":                  4,
    "senior data scientist":            4,
    "senior data engineer":             4,
    "senior ml engineer":               4,
    "senior ai engineer":               4,
    "senior machine learning engineer": 4,
    "senior backend engineer":          4,
    "senior devops engineer":           4,
    "senior research engineer":         4,
    "senior analyst":                   4,
    "team lead":                        4,
    "tech lead":                        4,

    # Lead / Staff
    "lead engineer":                    5,
    "lead data scientist":              5,
    "lead ml engineer":                 5,
    "lead ai engineer":                 5,
    "staff engineer":                   5,
    "staff software engineer":          5,
    "engineering manager":              5,
    "director of engineering":          5,

    # Principal / VP
    "principal engineer":               6,
    "principal data scientist":         6,
    "distinguished engineer":           6,
    "vp of engineering":                6,
    "cto":                              7,
    "chief architect":                  7,
}


def get_title_seniority(title: str) -> int:
    """Return seniority level (1-7) for a job title. Defaults to 3 (mid-level)."""
    cleaned = title.strip().lower()
    if cleaned in TITLE_SENIORITY:
        return TITLE_SENIORITY[cleaned]

    # Fuzzy matching: check if any known title is contained in the given title
    for known_title, level in sorted(TITLE_SENIORITY.items(),
                                     key=lambda x: -len(x[0])):
        if known_title in cleaned:
            return level

    return 3  # Default to mid-level


def get_hidden_requirements(concept: str) -> list[str]:
    """Return list of implied skills for a high-level JD concept."""
    cleaned = concept.strip().lower()
    return HIDDEN_REQUIREMENTS_MAP.get(cleaned, [])


def find_cluster_match(skill_a: str, skill_b: str) -> float:
    """Check if two skills belong to the same semantic cluster.

    Returns:
        1.0 if exact match
        CLUSTER_MATCH_WEIGHT if same cluster
        0.0 if no relationship
    """
    if skill_a == skill_b:
        return 1.0

    for cluster_skills in SEMANTIC_SKILL_CLUSTERS.values():
        if skill_a in cluster_skills and skill_b in cluster_skills:
            return CLUSTER_MATCH_WEIGHT

    return 0.0


# ---------------------------------------------------------------------------
# Industry relevance for AI roles
# ---------------------------------------------------------------------------
TECH_INDUSTRIES = {
    "software", "technology", "it services", "internet", "ai",
    "machine learning", "data analytics", "saas", "cloud computing",
    "fintech", "edtech", "healthtech",
}

NON_TECH_INDUSTRIES = {
    "manufacturing", "paper products", "retail", "hospitality",
    "real estate", "construction", "agriculture", "mining",
    "textiles", "food & beverage",
}


def get_industry_relevance(industry: str) -> float:
    """Return 0.0-1.0 relevance score for an industry to AI roles."""
    cleaned = industry.strip().lower()
    if cleaned in TECH_INDUSTRIES:
        return 1.0
    elif cleaned in NON_TECH_INDUSTRIES:
        return 0.2
    else:
        return 0.5  # Neutral / unknown

# ---------------------------------------------------------------------------
# Company size preference (product companies > services companies)
# The JD explicitly warns against pure consulting/services backgrounds
# ---------------------------------------------------------------------------
SERVICES_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "tech mahindra", "mindtree", "ltimindtree", "mphasis",
    "hexaware", "persistent systems", "cyient",
}


def is_services_company(company_name: str) -> bool:
    """Check if a company is a known IT services/consulting firm."""
    return company_name.strip().lower() in SERVICES_COMPANIES
