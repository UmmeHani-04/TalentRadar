"""
semantic_matcher.py — Semantic Matching Engine

Phase 2 deliverable. Uses sentence-transformers to compute embedding-based
similarity between a Job Description and candidate profiles.

The key advantage over keyword matching:
  - "Vector Database" matches FAISS, Pinecone, Qdrant, Weaviate, ChromaDB
  - "Production AI" matches deployment, MLOps, model serving
  - Career descriptions carry implicit signal about capabilities

Architecture:
  1. Build rich text representations for JD and each candidate
  2. Encode with all-MiniLM-L6-v2 (384-dim, fast on CPU)
  3. Compute cosine similarity → semantic_score (0-100)

Performance strategy:
  - Two-pass ranking: rule-based pre-filter → semantic on top candidates only
  - Batch encoding for efficiency
  - Single model load, reused across all candidates
"""

import numpy as np
from typing import Optional

from src.jd_parser import ParsedJD
from src.config import SEMANTIC_CONFIG


class SemanticMatcher:
    """Embedding-based semantic similarity scorer.

    Usage:
        matcher = SemanticMatcher()
        matcher.set_jd(parsed_jd)
        score = matcher.score_candidate(candidate_text)
        # or batch:
        scores = matcher.score_candidates_batch(candidate_texts)
    """

    def __init__(self, model_name: str | None = None):
        """Initialize the semantic matcher.

        Args:
            model_name: sentence-transformers model name.
                        Defaults to config value.
        """
        self.model_name = model_name or SEMANTIC_CONFIG["model_name"]
        self.model = None
        self.jd_embedding: Optional[np.ndarray] = None
        self._loaded = False

    def load_model(self) -> None:
        """Load the sentence-transformer model. Call once at startup."""
        if self._loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer
            print(f"[SemanticMatcher] Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self._loaded = True
            print(f"[SemanticMatcher] Model loaded successfully")
        except ImportError:
            print("[SemanticMatcher] WARNING: sentence-transformers not installed.")
            print("[SemanticMatcher] Falling back to TF-IDF based matching.")
            self._loaded = False

    def set_jd(self, parsed_jd: ParsedJD) -> None:
        """Compute and cache the JD embedding.

        Builds a rich text representation that captures both explicit
        requirements and implied context.
        """
        jd_text = self._build_jd_text(parsed_jd)

        if self._loaded and self.model is not None:
            self.jd_embedding = self.model.encode(
                jd_text, normalize_embeddings=True, show_progress_bar=False
            )
        else:
            # Fallback: store raw text for TF-IDF
            self._jd_text_fallback = jd_text
            self._build_tfidf_fallback()

    def _build_jd_text(self, parsed_jd: ParsedJD) -> str:
        """Build a rich text representation of the JD for embedding.

        Includes role, skills (weighted by importance), experience context,
        and key phrases that capture the JD's intent.
        """
        parts = [
            f"Job Role: {parsed_jd.role}",
            f"Seniority: {parsed_jd.seniority} level",
            f"Experience: {parsed_jd.experience_min} to {parsed_jd.experience_max} years",
        ]

        # Required skills get repeated for emphasis in embedding space
        if parsed_jd.required_skills:
            skills_text = ", ".join(parsed_jd.required_skills)
            parts.append(f"Required skills: {skills_text}")
            parts.append(f"Must have expertise in: {skills_text}")

        if parsed_jd.preferred_skills:
            parts.append(f"Preferred skills: {', '.join(parsed_jd.preferred_skills)}")

        if parsed_jd.hidden_requirements:
            parts.append(f"Related skills: {', '.join(parsed_jd.hidden_requirements)}")

        # Add context from the original JD (truncated for model limits)
        jd_snippet = parsed_jd.jd_text[:1500] if parsed_jd.jd_text else ""
        if jd_snippet:
            parts.append(f"Context: {jd_snippet}")

        return " | ".join(parts)

    def build_candidate_text(self, candidate: dict) -> str:
        """Build a rich text representation of a candidate for embedding.

        Combines profile headline, summary, skills, career descriptions,
        and education into a single text that captures the candidate's
        professional identity.
        """
        parts = []

        profile = candidate.get("profile", {})

        # Professional identity
        if profile.get("headline"):
            parts.append(f"Professional: {profile['headline']}")

        if profile.get("current_title"):
            parts.append(f"Current role: {profile['current_title']}")

        if profile.get("summary"):
            # Truncate long summaries
            summary = profile["summary"][:500]
            parts.append(f"Summary: {summary}")

        # Skills
        skills = candidate.get("skills", [])
        if skills:
            skill_names = [s["name"] for s in skills]
            # Weight by proficiency: advanced/expert skills mentioned twice
            high_prof = [s["name"] for s in skills
                        if s.get("proficiency") in ("advanced", "expert")]
            parts.append(f"Skills: {', '.join(skill_names)}")
            if high_prof:
                parts.append(f"Expert in: {', '.join(high_prof)}")

        # Career history (most recent first, limited)
        career = candidate.get("career_history", [])
        for job in career[:3]:  # Top 3 most recent
            job_text = f"{job.get('title', '')} at {job.get('company', '')}"
            if job.get("description"):
                job_text += f": {job['description'][:200]}"
            parts.append(job_text)

        # Education
        education = candidate.get("education", [])
        for edu in education[:2]:
            parts.append(
                f"Education: {edu.get('degree', '')} in "
                f"{edu.get('field_of_study', '')} from {edu.get('institution', '')}"
            )

        # Certifications
        certs = candidate.get("certifications", [])
        if certs:
            cert_names = [c["name"] for c in certs]
            parts.append(f"Certifications: {', '.join(cert_names)}")

        return " | ".join(parts)

    def score_candidate(self, candidate_text: str) -> float:
        """Score a single candidate's text against the JD.

        Returns:
            Semantic similarity score on a 0-100 scale.
        """
        if self._loaded and self.model is not None and self.jd_embedding is not None:
            cand_embedding = self.model.encode(
                candidate_text, normalize_embeddings=True, show_progress_bar=False
            )
            similarity = float(np.dot(self.jd_embedding, cand_embedding))
            # Cosine similarity is [-1, 1], but for text it's usually [0, 1]
            # Scale to 0-100
            return max(0.0, min(100.0, similarity * 100))
        else:
            return self._tfidf_score(candidate_text)

    def score_candidates_batch(self, candidate_texts: list[str]) -> list[float]:
        """Score multiple candidates in a single batch for efficiency.

        Args:
            candidate_texts: List of candidate text representations.

        Returns:
            List of semantic similarity scores (0-100 scale).
        """
        if not candidate_texts:
            return []

        if self._loaded and self.model is not None and self.jd_embedding is not None:
            batch_size = SEMANTIC_CONFIG["batch_size"]
            all_scores = []

            for i in range(0, len(candidate_texts), batch_size):
                batch = candidate_texts[i:i + batch_size]
                embeddings = self.model.encode(
                    batch,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                    batch_size=batch_size,
                )
                # Cosine similarity with pre-normalized vectors = dot product
                similarities = np.dot(embeddings, self.jd_embedding)
                scores = np.clip(similarities * 100, 0, 100).tolist()
                all_scores.extend(scores)

            return all_scores
        else:
            return [self._tfidf_score(text) for text in candidate_texts]

    # -------------------------------------------------------------------
    # TF-IDF fallback (when sentence-transformers is not available)
    # -------------------------------------------------------------------
    def _build_tfidf_fallback(self) -> None:
        """Build TF-IDF vectorizer as fallback."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._tfidf = TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2),
            )
            self._tfidf.fit([self._jd_text_fallback])
            self._jd_tfidf = self._tfidf.transform([self._jd_text_fallback])
            self._has_tfidf = True
        except ImportError:
            self._has_tfidf = False

    def _tfidf_score(self, candidate_text: str) -> float:
        """Score using TF-IDF cosine similarity (fallback)."""
        if hasattr(self, '_has_tfidf') and self._has_tfidf:
            from sklearn.metrics.pairwise import cosine_similarity
            cand_vec = self._tfidf.transform([candidate_text])
            sim = cosine_similarity(self._jd_tfidf, cand_vec)[0][0]
            return max(0.0, min(100.0, sim * 100))
        return 50.0  # Neutral score if no matching available


# ===========================================================================
# Standalone test
# ===========================================================================
if __name__ == "__main__":
    from src.config import JD_TEXT
    from src.jd_parser import parse_jd
    import json

    parsed = parse_jd(JD_TEXT)
    matcher = SemanticMatcher()
    matcher.load_model()
    matcher.set_jd(parsed)

    # Test with a sample candidate text
    test_text = (
        "ML Engineer at a product company. 6 years experience. "
        "Expert in Python, PyTorch, sentence-transformers, FAISS, Qdrant. "
        "Built end-to-end ranking system for job matching platform."
    )
    score = matcher.score_candidate(test_text)
    print(f"Test candidate semantic score: {score:.1f}/100")
