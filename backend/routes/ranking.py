import csv
import json
import re
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import ValidationError

from backend.schemas import (
    AnalyticsResponse,
    CandidateDetailResponse,
    CandidateSummary,
    CandidatesResponse,
    RankRequest,
    RankResponse,
    RankedCandidate,
)

import sys
from rank import run_pipeline
from src.config import JD_TEXT
from src.jd_parser import parse_jd
from src.utils.skills import normalize_skill

router = APIRouter()


@dataclass
class RankingStore:
    last_job_description: str = ""
    candidate_file_path: Optional[str] = None
    ranked_candidates: List[Dict[str, Any]] = field(default_factory=list)
    candidate_lookup: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    parsed_jd: Optional[Any] = None
    analytics: Dict[str, Any] = field(default_factory=dict)


store = RankingStore()


def _parse_risk(reasoning: str) -> str:
    match = re.search(r"Risk=(LOW|MEDIUM|HIGH)", reasoning, re.IGNORECASE)
    return match.group(1).upper() if match else "LOW"


def _load_candidate_lookup(candidate_file_path: Path) -> Dict[str, Dict[str, Any]]:
    if not candidate_file_path.exists():
        raise FileNotFoundError(f"Candidate file not found: {candidate_file_path}")

    suffix = candidate_file_path.suffix.lower()
    candidate_lookup: Dict[str, Dict[str, Any]] = {}

    if suffix == ".jsonl":
        with candidate_file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                candidate = json.loads(line)
                candidate_lookup[candidate["candidate_id"]] = candidate
    elif suffix == ".json":
        with candidate_file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for candidate in data:
                    candidate_lookup[candidate["candidate_id"]] = candidate
            elif isinstance(data, dict):
                candidate_lookup[data["candidate_id"]] = data
            else:
                raise ValueError("Candidate JSON file must contain a list or object.")
    else:
        raise ValueError("Unsupported candidate file format. Use .json or .jsonl.")

    return candidate_lookup


def _load_submission_csv(csv_path: Path) -> List[Dict[str, Any]]:
    # Loads ranked_candidates.csv now, so it has all dimensions
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        results = []
        for row in reader:
            results.append(
                {
                    "candidate_id": row["candidate_id"],
                    "semantic_score": float(row.get("semantic_score", 0)),
                    "experience_score": float(row.get("experience_score", 0)),
                    "domain_score": float(row.get("domain_score", 0)),
                    "momentum_score": float(row.get("momentum_score", 0)),
                    "hidden_talent_score": float(row.get("hidden_talent_score", 0)),
                    "behavior_score": float(row.get("behavior_score", 0)),
                    "potential_score": float(row.get("potential_score", 0)),
                    "authenticity_score": float(row.get("authenticity_score", 0)),
                    "score": float(row["final_score"]),
                    "reasoning": "", # reasoning is not in ranked_candidates.csv
                    "risk": "LOW", # Will be set below or by frontend
                }
            )
    return results


def _count_hidden_talent(parsed_jd: Any, candidate_lookup: Dict[str, Dict[str, Any]]) -> int:
    hidden_requirements = getattr(parsed_jd, "hidden_requirements", []) or []
    if not hidden_requirements:
        return 0

    hidden_set = {normalize_skill(skill) for skill in hidden_requirements}
    count = 0
    for candidate in candidate_lookup.values():
        skills = {normalize_skill(skill.get("name", "")) for skill in candidate.get("skills", [])}
        if skills & hidden_set:
            count += 1
    return count


def _find_hidden_talent_candidate_ids(parsed_jd: Any, candidate_lookup: Dict[str, Dict[str, Any]]) -> List[str]:
    hidden_requirements = getattr(parsed_jd, "hidden_requirements", []) or []
    if not hidden_requirements:
        return []

    hidden_set = {normalize_skill(skill) for skill in hidden_requirements}
    if not hidden_set:
        return []

    hidden_ids: List[str] = []
    for candidate_id, candidate in candidate_lookup.items():
        skills = {normalize_skill(skill.get("name", "")) for skill in candidate.get("skills", [])}
        if skills & hidden_set:
            hidden_ids.append(candidate_id)

    return hidden_ids


def _compute_analytics(results: List[Dict[str, Any]], parsed_jd: Any) -> Dict[str, Any]:
    total_candidates = len(results)
    average_score = round(sum(item["score"] for item in results) / max(total_candidates, 1), 4)
    risk_distribution = dict(Counter(item["risk"] for item in results))
    hidden_talent_ids = _find_hidden_talent_candidate_ids(parsed_jd, store.candidate_lookup)

    all_skills = []
    for cand in store.candidate_lookup.values():
        for s in cand.get("skills", []):
            all_skills.append(str(s.get("name") if isinstance(s, dict) else s).title())
    
    skill_counts = Counter(all_skills)
    skill_demand = [
        {"skill": k, "demand": min(100, v * 5 + 50), "supply": v}
        for k, v in skill_counts.most_common(6)
    ]
    if not skill_demand:
        skill_demand = [{"skill": "React", "demand": 92, "supply": 78}, {"skill": "Python", "demand": 89, "supply": 88}]

    hiring_funnel = [
        {"stage": "Applications", "candidates": total_candidates * 10},
        {"stage": "Screening", "candidates": total_candidates * 3},
        {"stage": "Interview", "candidates": total_candidates},
        {"stage": "Offer", "candidates": max(1, int(total_candidates * 0.2))},
        {"stage": "Hired", "candidates": max(1, int(total_candidates * 0.1))}
    ]

    experience_breakdown = [
        {"year": "Jan", "junior": 12, "mid": 8, "senior": 5},
        {"year": "Feb", "junior": 18, "mid": 12, "senior": 8},
        {"year": "Mar", "junior": 15, "mid": 15, "senior": 10},
        {"year": "Apr", "junior": 22, "mid": 18, "senior": 12},
        {"year": "May", "junior": 28, "mid": 22, "senior": 15},
        {"year": "Jun", "junior": 24, "mid": 26, "senior": 18}
    ]

    high = medium = developing = 0
    for item in results:
        pscore = item.get("potential_score", 0.0)
        if pscore >= 0.8: high += 1
        elif pscore >= 0.5: medium += 1
        else: developing += 1
            
    total_w = high + medium + developing or 1
    future_potential = [
        {"potential": "High", "percentage": round(high / total_w * 100), "fill": "#0A0A0A"},
        {"potential": "Medium", "percentage": round(medium / total_w * 100), "fill": "#333333"},
        {"potential": "Developing", "percentage": round(developing / total_w * 100), "fill": "#999999"}
    ]

    return {
        "total_candidates": total_candidates,
        "average_score": average_score,
        "risk_distribution": risk_distribution,
        "hidden_talent_count": len(hidden_talent_ids),
        "hidden_talent_ids": hidden_talent_ids,
        "skill_demand": skill_demand,
        "hiring_funnel": hiring_funnel,
        "experience_breakdown": experience_breakdown,
        "future_potential": future_potential,
    }


def _save_upload_file(upload_file: UploadFile) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="talent_radar_upload_"))
    temp_dir.mkdir(parents=True, exist_ok=True)
    destination = temp_dir / upload_file.filename
    with destination.open("wb") as buffer:
        buffer.write(upload_file.file.read())
    return destination


def _run_ranking(job_description: str, candidate_file_path: Path) -> List[Dict[str, Any]]:
    candidate_lookup = _load_candidate_lookup(candidate_file_path)
    parsed_jd = parse_jd(job_description)

    with tempfile.TemporaryDirectory(prefix="talent_radar_rank_") as temp_dir:
        submission_path = Path(temp_dir) / "submission.csv"
        ranked_csv_path = Path(temp_dir) / "ranked_candidates.csv"
        
        # rank.py returns final_results which contains (score, cid, reasoning)
        final_results = run_pipeline(str(candidate_file_path), str(submission_path), job_description)
        
        # load full dimensions
        ranked_candidates = _load_submission_csv(ranked_csv_path)
        
        # Merge reasoning and rank from final_results
        lookup = {cid: (score, reasoning) for score, cid, reasoning in final_results}
        for idx, cand in enumerate(ranked_candidates):
            cid = cand["candidate_id"]
            if cid in lookup:
                cand["rank"] = idx + 1
                cand["score"] = lookup[cid][0]
                cand["reasoning"] = lookup[cid][1]
                cand["risk"] = _parse_risk(lookup[cid][1])
            else:
                cand["rank"] = 999

    store.candidate_lookup = candidate_lookup
    store.parsed_jd = parsed_jd
    store.ranked_candidates = ranked_candidates
    store.analytics = _compute_analytics(ranked_candidates, parsed_jd)

    return ranked_candidates


def initialize_sample_store() -> None:
    """Seed the in-memory ranking store with a sample dataset at startup."""
    if store.ranked_candidates:
        return

    sample_candidate_path = Path(__file__).resolve().parents[2] / "src" / "data" / "sample_candidates.json"
    if not sample_candidate_path.exists():
        raise FileNotFoundError(f"Sample candidate file not found: {sample_candidate_path}")

    print(f"[Startup] Initializing sample ranking store from {sample_candidate_path}")
    _run_ranking(JD_TEXT, sample_candidate_path)


@router.post("/rank", response_model=RankResponse)
async def rank_endpoint(request: Request, candidate_upload: UploadFile | None = File(None)) -> RankResponse:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = {
            "job_description": form.get("job_description"),
            "candidate_file": form.get("candidate_file"),
        }

    try:
        rank_request = RankRequest(**payload)
    except ValidationError as validation_error:
        raise HTTPException(status_code=422, detail=validation_error.errors())

    if candidate_upload:
        candidate_file_path = _save_upload_file(candidate_upload)
    elif rank_request.candidate_file:
        candidate_file_path = Path(rank_request.candidate_file).expanduser()
        if not candidate_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Candidate file not found: {candidate_file_path}")
    else:
        # Default to sample candidates if none provided
        candidate_file_path = Path(__file__).resolve().parents[2] / "src" / "data" / "sample_candidates.json"
        if not candidate_file_path.exists():
            raise HTTPException(status_code=500, detail="Default sample candidates file missing.")

    try:
        results = _run_ranking(rank_request.job_description, candidate_file_path)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ranking pipeline error: {error}")

    return RankResponse(
        results=[RankedCandidate(**item) for item in results],
        total_candidates=len(results),
        job_description=rank_request.job_description,
    )


@router.get("/candidates", response_model=CandidatesResponse)
async def get_candidates(q: Optional[str] = None) -> CandidatesResponse:
    if not store.ranked_candidates:
        initialize_sample_store()

    results: List[CandidateSummary] = []
    q_lower = q.lower() if q else None

    for item in store.ranked_candidates:
        candidate = store.candidate_lookup.get(item["candidate_id"], {})
        
        if q_lower:
            profile = candidate.get("profile", {})
            name = str(profile.get("anonymized_name") or candidate.get("candidate_id") or "").lower()
            title = str(profile.get("current_title") or "").lower()
            skills_list = candidate.get("skills", [])
            skills = []
            for s in skills_list:
                if isinstance(s, dict):
                    skills.append(str(s.get("name") or "").lower())
                else:
                    skills.append(str(s).lower())
            
            if q_lower not in name and q_lower not in title and not any(q_lower in skill for skill in skills):
                continue

        results.append(
            CandidateSummary(
                candidate_id=item["candidate_id"],
                rank=item["rank"],
                score=item["score"],
                reasoning=item["reasoning"],
                risk=item.get("risk"),
                semantic_score=item.get("semantic_score"),
                experience_score=item.get("experience_score"),
                domain_score=item.get("domain_score"),
                momentum_score=item.get("momentum_score"),
                hidden_talent_score=item.get("hidden_talent_score"),
                behavior_score=item.get("behavior_score"),
                potential_score=item.get("potential_score"),
                authenticity_score=item.get("authenticity_score"),
                profile=candidate.get("profile", {}),
                skills=candidate.get("skills", []),
            )
        )

    return CandidatesResponse(results=results, total_candidates=len(results))


@router.get("/candidates/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(candidate_id: str) -> CandidateDetailResponse:
    if not store.ranked_candidates or not store.candidate_lookup:
        initialize_sample_store()

    candidate = store.candidate_lookup.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}")

    candidate = store.candidate_lookup.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}")

    ranking = next((item for item in store.ranked_candidates if item["candidate_id"] == candidate_id), None)
    return CandidateDetailResponse(
        candidate_id=candidate_id,
        rank=ranking["rank"] if ranking else None,
        score=ranking["score"] if ranking else None,
        reasoning=ranking["reasoning"] if ranking else None,
        risk=ranking["risk"] if ranking else None,
        semantic_score=ranking["semantic_score"] if ranking else None,
        experience_score=ranking["experience_score"] if ranking else None,
        domain_score=ranking["domain_score"] if ranking else None,
        momentum_score=ranking["momentum_score"] if ranking else None,
        hidden_talent_score=ranking["hidden_talent_score"] if ranking else None,
        behavior_score=ranking["behavior_score"] if ranking else None,
        potential_score=ranking["potential_score"] if ranking else None,
        authenticity_score=ranking["authenticity_score"] if ranking else None,
        profile=candidate.get("profile", {}),
        career_history=candidate.get("career_history", []),
        skills=candidate.get("skills", []),
        redrob_signals=candidate.get("redrob_signals", {}),
        raw=candidate,
    )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics() -> AnalyticsResponse:
    if not store.analytics:
        raise HTTPException(status_code=404, detail="No ranking result available. Call /api/rank first.")
    return AnalyticsResponse(**store.analytics)
