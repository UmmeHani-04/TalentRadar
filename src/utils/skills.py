"""
skills.py — Comprehensive skill taxonomy, normalization, and proficiency weights.

This module is the backbone of accurate skill matching. It maps the messy real-world
of how people list skills on profiles to a clean, matchable representation.

Key design decisions:
- Skills are grouped into DOMAINS for contextual matching
- Aliases resolve common abbreviations and variations
- Proficiency weights give graduated credit (not binary match/no-match)
"""

# ---------------------------------------------------------------------------
# Proficiency → numeric weight
# ---------------------------------------------------------------------------
PROFICIENCY_WEIGHTS = {
    "beginner":     0.30,
    "intermediate": 0.60,
    "advanced":     0.85,
    "expert":       1.00,
}

# ---------------------------------------------------------------------------
# Skill alias map: variant → canonical name
# All lookups should go through normalize_skill() below.
# ---------------------------------------------------------------------------
SKILL_ALIASES = {
    # Python ecosystem
    "py":               "python",
    "python3":          "python",
    "python 3":         "python",
    "cpython":          "python",
    "pyspark":          "spark",
    "apache spark":     "spark",
    "apache kafka":     "kafka",
    "apache airflow":   "airflow",
    "apache beam":      "beam",
    "apache flink":     "flink",

    # ML/AI
    "ml":               "machine learning",
    "ai":               "artificial intelligence",
    "deep learning":    "deep learning",
    "dl":               "deep learning",
    "nlp":              "natural language processing",
    "natural language processing": "natural language processing",
    "cv":               "computer vision",
    "llm":              "large language models",
    "llms":             "large language models",
    "large language model": "large language models",
    "large language models": "large language models",
    "fine-tuning llms": "llm fine-tuning",
    "fine tuning llms": "llm fine-tuning",
    "lora":             "llm fine-tuning",
    "qlora":            "llm fine-tuning",
    "peft":             "llm fine-tuning",
    "rag":              "retrieval augmented generation",
    "retrieval augmented generation": "retrieval augmented generation",
    "retrieval systems": "information retrieval",
    "information retrieval": "information retrieval",
    "search systems":   "information retrieval",
    "ranking systems":  "ranking",
    "learning to rank": "ranking",
    "recommendation systems": "recommendation systems",
    "recommender systems": "recommendation systems",

    # Vector databases
    "vector databases": "vector databases",
    "vector db":        "vector databases",
    "vector database":  "vector databases",
    "faiss":            "faiss",
    "pinecone":         "pinecone",
    "qdrant":           "qdrant",
    "weaviate":         "weaviate",
    "milvus":           "milvus",
    "chromadb":         "chromadb",
    "chroma":           "chromadb",

    # Frameworks
    "tensorflow":       "tensorflow",
    "tf":               "tensorflow",
    "pytorch":          "pytorch",
    "torch":            "pytorch",
    "keras":            "keras",
    "scikit-learn":     "scikit-learn",
    "sklearn":          "scikit-learn",
    "huggingface":      "hugging face",
    "hugging face":     "hugging face",
    "hf":               "hugging face",
    "transformers":     "transformers",
    "sentence-transformers": "sentence transformers",
    "sentence transformers": "sentence transformers",
    "langchain":        "langchain",
    "llamaindex":       "llamaindex",
    "xgboost":          "xgboost",
    "lightgbm":         "lightgbm",
    "catboost":         "catboost",

    # Cloud & DevOps
    "aws":              "aws",
    "amazon web services": "aws",
    "gcp":              "gcp",
    "google cloud":     "gcp",
    "google cloud platform": "gcp",
    "azure":            "azure",
    "microsoft azure":  "azure",
    "docker":           "docker",
    "k8s":              "kubernetes",
    "kubernetes":       "kubernetes",
    "ci/cd":            "ci/cd",
    "cicd":             "ci/cd",
    "jenkins":          "ci/cd",
    "github actions":   "ci/cd",
    "terraform":        "terraform",
    "ansible":          "ansible",
    "monitoring":       "monitoring",
    "prometheus":       "monitoring",
    "grafana":          "monitoring",
    "datadog":          "monitoring",
    "mlflow":           "mlflow",
    "weights & biases": "wandb",
    "wandb":            "wandb",
    "bentoml":          "bentoml",

    # Databases
    "sql":              "sql",
    "mysql":            "sql",
    "postgresql":       "postgresql",
    "postgres":         "postgresql",
    "mongodb":          "mongodb",
    "mongo":            "mongodb",
    "redis":            "redis",
    "elasticsearch":    "elasticsearch",
    "opensearch":       "opensearch",
    "snowflake":        "snowflake",
    "bigquery":         "bigquery",
    "databricks":       "databricks",

    # Data Engineering
    "dbt":              "dbt",
    "data pipelines":   "data engineering",
    "etl":              "data engineering",
    "data engineering":  "data engineering",

    # Web/General (non-AI, for negative signal)
    "react":            "react",
    "angular":          "angular",
    "vue":              "vue",
    "node.js":          "node.js",
    "nodejs":           "node.js",
    "javascript":       "javascript",
    "js":               "javascript",
    "typescript":       "typescript",
    "ts":               "typescript",
    "html":             "html",
    "css":              "css",
    "tailwind":         "tailwind",
    "webpack":          "webpack",
    "redux":            "redux",
    "graphql":          "graphql",
    "flask":            "flask",
    "django":           "django",
    "fastapi":          "fastapi",

    # Non-tech
    "excel":            "excel",
    "powerpoint":       "powerpoint",
    "photoshop":        "photoshop",
    "seo":              "seo",
    "marketing":        "marketing",
    "content writing":  "content writing",
    "project management": "project management",
    "six sigma":        "six sigma",
    "sap":              "sap",
    "accounting":       "accounting",

    # ML techniques
    "gans":             "gans",
    "image classification": "image classification",
    "object detection": "object detection",
    "speech recognition": "speech recognition",
    "tts":              "text to speech",
    "text to speech":   "text to speech",
    "statistical modeling": "statistical modeling",
    "feature engineering": "feature engineering",
}

# ---------------------------------------------------------------------------
# Skill domains — used to understand WHAT KIND of skill a candidate has
# ---------------------------------------------------------------------------
SKILL_DOMAINS = {
    "ai_core": {
        "machine learning", "deep learning", "natural language processing",
        "large language models", "llm fine-tuning", "information retrieval",
        "ranking", "recommendation systems", "retrieval augmented generation",
        "transformers", "sentence transformers", "hugging face",
    },
    "ai_tools": {
        "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost",
        "lightgbm", "catboost", "langchain", "llamaindex", "mlflow",
        "wandb", "bentoml",
    },
    "vector_db": {
        "vector databases", "faiss", "pinecone", "qdrant", "weaviate",
        "milvus", "chromadb", "elasticsearch", "opensearch",
    },
    "data_engineering": {
        "spark", "kafka", "airflow", "beam", "flink", "data engineering",
        "sql", "postgresql", "mongodb", "redis", "snowflake", "bigquery",
        "databricks", "dbt",
    },
    "cloud_devops": {
        "aws", "gcp", "azure", "docker", "kubernetes", "ci/cd",
        "terraform", "ansible", "monitoring",
    },
    "programming": {
        "python", "javascript", "typescript", "node.js", "flask",
        "django", "fastapi",
    },
    "frontend": {
        "react", "angular", "vue", "html", "css", "tailwind",
        "webpack", "redux", "graphql",
    },
    "non_tech": {
        "excel", "powerpoint", "photoshop", "seo", "marketing",
        "content writing", "project management", "six sigma", "sap",
        "accounting",
    },
    "ml_specialized": {
        "computer vision", "gans", "image classification",
        "object detection", "speech recognition", "text to speech",
        "statistical modeling", "feature engineering",
    },
}


def normalize_skill(skill_name: str) -> str:
    """Normalize a skill name to its canonical form.

    Handles case-insensitivity, whitespace, and alias resolution.
    """
    cleaned = skill_name.strip().lower()
    return SKILL_ALIASES.get(cleaned, cleaned)


def get_skill_domain(canonical_skill: str) -> str | None:
    """Return the domain a skill belongs to, or None if unknown."""
    for domain, skills in SKILL_DOMAINS.items():
        if canonical_skill in skills:
            return domain
    return None


def get_proficiency_weight(proficiency: str) -> float:
    """Return numeric weight for a proficiency level."""
    return PROFICIENCY_WEIGHTS.get(proficiency.lower().strip(), 0.3)


def is_ai_relevant(canonical_skill: str) -> bool:
    """Check if a skill is relevant to AI/ML roles."""
    domain = get_skill_domain(canonical_skill)
    return domain in {"ai_core", "ai_tools", "vector_db", "data_engineering",
                      "cloud_devops", "programming", "ml_specialized"}


def is_non_tech(canonical_skill: str) -> bool:
    """Check if a skill is non-technical (negative signal for AI roles)."""
    domain = get_skill_domain(canonical_skill)
    return domain in {"non_tech", "frontend"}
