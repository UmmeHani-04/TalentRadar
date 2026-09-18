from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RankRequest(BaseModel):
    job_description: str = Field(..., title="Job description text")
    candidate_file: Optional[str] = Field(
        None,
        title="Candidate file path",
        description="Local path to a candidate JSON/JSONL file. Use this or upload a file.",
    )


class RankedCandidate(BaseModel):
    candidate_id: str
    rank: int
    score: float
    reasoning: str
    risk: Optional[str] = None


class RankResponse(BaseModel):
    results: List[RankedCandidate]
    total_candidates: int
    job_description: str


class CandidateSummary(BaseModel):
    candidate_id: str
    rank: int
    score: float
    reasoning: str
    risk: Optional[str] = None
    semantic_score: Optional[float] = None
    experience_score: Optional[float] = None
    domain_score: Optional[float] = None
    momentum_score: Optional[float] = None
    hidden_talent_score: Optional[float] = None
    behavior_score: Optional[float] = None
    potential_score: Optional[float] = None
    authenticity_score: Optional[float] = None
    profile: Dict[str, Any] = Field(default_factory=dict)
    skills: List[Dict[str, Any]] = Field(default_factory=list)


class CandidateDetailResponse(BaseModel):
    candidate_id: str
    rank: Optional[int]
    score: Optional[float]
    reasoning: Optional[str]
    risk: Optional[str] = None
    semantic_score: Optional[float] = None
    experience_score: Optional[float] = None
    domain_score: Optional[float] = None
    momentum_score: Optional[float] = None
    hidden_talent_score: Optional[float] = None
    behavior_score: Optional[float] = None
    potential_score: Optional[float] = None
    authenticity_score: Optional[float] = None
    profile: Dict[str, Any] = Field(default_factory=dict)
    career_history: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    redrob_signals: Dict[str, Any] = Field(default_factory=dict)
    raw: Dict[str, Any] = Field(default_factory=dict)


class CandidatesResponse(BaseModel):
    results: List[CandidateSummary]
    total_candidates: int


class AnalyticsResponse(BaseModel):
    total_candidates: int
    average_score: float
    risk_distribution: Dict[str, int]
    hidden_talent_count: int
    hidden_talent_ids: List[str] = Field(default_factory=list)
    skill_demand: List[Dict[str, Any]] = Field(default_factory=list)
    hiring_funnel: List[Dict[str, Any]] = Field(default_factory=list)
    experience_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    future_potential: List[Dict[str, Any]] = Field(default_factory=list)
