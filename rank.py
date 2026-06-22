"""
rank.py — Main Pipeline Entry Point

╔══════════════════════════════════════════════════════════════════════════════╗
║  TEAM STRUCTURE & PIPELINE FLOW                                            ║
║                                                                            ║
║  Job Description                                                           ║
║       ↓                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  👩 SEEMA — JD Understanding + Matching Logic                      │   ║
║  │    • JD parsing & skill extraction   → src/jd_parser.py           │   ║
║  │    • Hidden requirement detection    → src/utils/mappings.py      │   ║
║  │    • Semantic matching (embeddings)  → src/semantic_matcher.py     │   ║
║  │    • Scoring formula & weights       → src/config.py              │   ║
║  │    • Skill taxonomy & normalization  → src/utils/skills.py        │   ║
║  │    • Cluster mappings & title ladder → src/utils/mappings.py      │   ║
║  └────────────────────────────────┬────────────────────────────────────┘   ║
║       ↓  parsed_jd + semantic scores                                      ║
║  Candidate Data                                                            ║
║       ↓                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  👨 VIVEK — Candidate Analysis + Scoring                           │   ║
║  │    • Candidate feature extraction                                  │   ║
║  │    • Hidden talent detection                                       │   ║
║  │    • Skill authenticity checks                                     │   ║
║  │    • Generate candidate-level scores                               │   ║
║  │                                                                    │   ║
║  │    Search for:  ▼▼▼ VIVEK INTEGRATION POINT ▼▼▼                   │   ║
║  │    Currently: src/ranker.py has Seema's reference scorer.          │   ║
║  │    Vivek can extend/replace candidate scoring logic there.         │   ║
║  └────────────────────────────────┬────────────────────────────────────┘   ║
║       ↓  ranked_candidates (scored + sorted)                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  👤 3RD TEAMMATE — Risk + Explainability + Dashboard               │   ║
║  │    • Risk assessment layer                                         │   ║
║  │    • Explainability / reasoning enrichment                         │   ║
║  │    • Dashboard / visualization                                     │   ║
║  │                                                                    │   ║
║  │    Search for:  ▼▼▼ TEAMMATE-3 INTEGRATION POINT ▼▼▼              │   ║
║  │    Input: final_results list + candidate_data dicts                │   ║
║  └────────────────────────────────┬────────────────────────────────────┘   ║
║       ↓                                                                    ║
║  submission.csv (top 100)                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

End-to-end ranking pipeline:
  1. [SEEMA]    Parse the Job Description → extract skills, experience, hidden reqs
  2. [SEEMA]    Load Semantic Matcher → sentence-transformers embeddings
  3. [SEEMA]    Stream candidates + fast rule-based pre-filter → top 5000
  4. [SEEMA]    Semantic scoring on top-5000 → cosine similarity
  5. [VIVEK]    Candidate-level scoring → feature extraction, authenticity, talents
  6. [TEAM-3]   Risk assessment + explainability enrichment
  7.            Generate top-100 output CSV

Usage:
  python rank.py --candidates ./candidates.jsonl --out ./submission.csv
  python rank.py --candidates ./src/data/sample_candidates.json --out ./test_submission.csv
"""

import argparse
import csv
import heapq
import json
import sys
import time
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import JD_TEXT, PIPELINE_CONFIG, SEMANTIC_CONFIG
from src.jd_parser import parse_jd
from src.semantic_matcher import SemanticMatcher
from src.ranker import rank_candidate, CandidateScore, compute_final_score
from src.risk_module import assess_risk



def load_candidates(filepath: str):
    """Stream candidates from JSONL or JSON file.

    Yields one candidate dict at a time (memory-efficient for large files).
    """
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: Candidate file not found: {filepath}")
        sys.exit(1)

    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"WARNING: Skipping malformed line {line_num}: {e}")
    elif suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                yield from data
            else:
                yield data
    else:
        print(f"ERROR: Unsupported file format: {suffix}. Use .jsonl or .json")
        sys.exit(1)


def write_submission(candidates: list[tuple[float, str, str]],
                     output_path: str) -> None:
    """Write top-100 ranked candidates to submission CSV.

    Args:
        candidates: List of (score, candidate_id, reasoning) sorted by score desc.
        output_path: Path to output CSV file.
    """
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for rank, (score, cid, reasoning) in enumerate(candidates[:100], 1):
            writer.writerow([cid, rank, f"{score:.4f}", reasoning])

    print(f"[Pipeline] Submission written to {output_path}")


def write_ranked_csv(scored: list[CandidateScore], output_path: str) -> None:
    """Write ranked candidates with per-dimension scores (team deliverable).

    Output format:
        candidate_id, semantic_score, skill_score, experience_score,
        career_score, behavior_score, final_score

    This is the format the team uses for handoff between modules.
    """
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "candidate_id", "semantic_score", "skill_score",
            "experience_score", "career_score", "behavior_score",
            "final_score"
        ])

        for sc in scored:
            writer.writerow([
                sc.candidate_id,
                f"{sc.semantic_score:.1f}",
                f"{sc.skill_score:.1f}",
                f"{sc.experience_score:.1f}",
                f"{sc.career_score:.1f}",
                f"{sc.behavior_score:.1f}",
                f"{sc.final_score:.4f}",
            ])

    print(f"[Pipeline] Ranked candidates written to {output_path}")


def run_pipeline(candidates_path: str, output_path: str, jd_text: str = None):
    """Execute the full ranking pipeline.

    Two-pass architecture for speed on 100K+ candidates:
      Pass 1: Fast rule-based scoring (skills + experience + career + behavior)
              → Keep top N candidates (default: 5000)
      Pass 2: Semantic scoring on top N only
              → Re-rank with combined scores → Output top 100
    """
    start_time = time.time()

    # ---- Step 1: Parse JD → parsed_jd.json ----
    print("[Pipeline] Step 1: Parsing Job Description...")
    jd = jd_text or JD_TEXT
    parsed_jd = parse_jd(jd)
    print(f"  Role: {parsed_jd.role}")
    print(f"  Required skills: {parsed_jd.required_skills}")
    print(f"  Experience: {parsed_jd.experience_min}-{parsed_jd.experience_max} years")
    print(f"  Hidden requirements: {parsed_jd.hidden_requirements}")

    # ── OUTPUT 1: parsed_jd.json (team deliverable) ──
    output_dir = Path(output_path).parent
    jd_json_path = output_dir / "parsed_jd.json"
    with open(jd_json_path, "w", encoding="utf-8") as f:
        json.dump(parsed_jd.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"  -> Saved parsed JD to {jd_json_path}")

    # ---- Step 2: Initialize Semantic Matcher ----
    print("\n[Pipeline] Step 2: Loading Semantic Matcher...")
    matcher = SemanticMatcher()
    matcher.load_model()
    matcher.set_jd(parsed_jd)

    # ---- Step 3: Pass 1 — Fast rule-based pre-filter ----
    print("\n[Pipeline] Step 3: Pass 1 — Rule-based scoring...")
    prefilter_n = SEMANTIC_CONFIG["prefilter_top_n"]

    # Use a min-heap of size prefilter_n to keep top candidates
    # Heap elements: (score, candidate_id, candidate_dict)
    top_heap: list[tuple[float, str, dict]] = []
    total_candidates = 0

    for candidate in load_candidates(candidates_path):
        total_candidates += 1

        if total_candidates % 10000 == 0:
            print(f"  Processed {total_candidates} candidates...")

        # Quick rule-based score (no semantic — faster)
        result = rank_candidate(candidate, parsed_jd, semantic_score=50.0)
        quick_score = result.final_score

        # Maintain top-N heap
        if len(top_heap) < prefilter_n:
            heapq.heappush(top_heap, (quick_score, candidate["candidate_id"], candidate))
        elif quick_score > top_heap[0][0]:
            heapq.heapreplace(top_heap, (quick_score, candidate["candidate_id"], candidate))

    elapsed_pass1 = time.time() - start_time
    print(f"  Pass 1 complete: {total_candidates} candidates -> top {len(top_heap)} "
          f"in {elapsed_pass1:.1f}s")

    # ---- Step 4: Pass 2 — Semantic scoring on top-N ----
    print(f"\n[Pipeline] Step 4: Pass 2 — Semantic scoring on top {len(top_heap)}...")
    pass2_start = time.time()

    # Sort heap (it's a min-heap, so pop all)
    top_candidates = sorted(top_heap, key=lambda x: -x[0])

    # Build candidate texts for batch semantic scoring
    candidate_texts = []
    candidate_data = []
    for score, cid, cand in top_candidates:
        text = matcher.build_candidate_text(cand)
        candidate_texts.append(text)
        candidate_data.append(cand)

    # Batch semantic scoring
    semantic_scores = matcher.score_candidates_batch(candidate_texts)

    # ---- Step 5: Final re-ranking with semantic scores ----
    print("\n[Pipeline] Step 5: Final ranking with semantic scores...")
    final_results: list[tuple[float, str, str]] = []
    scored_candidates: list[CandidateScore] = []  # Full score breakdowns

    for i, (cand, sem_score) in enumerate(zip(candidate_data, semantic_scores)):
        result = rank_candidate(cand, parsed_jd, semantic_score=sem_score)
        final_results.append((result.final_score, result.candidate_id, result.reasoning))
        scored_candidates.append(result)

    # Sort by score descending, then by candidate_id ascending (for tie-breaking)
    sort_order = sorted(range(len(final_results)),
                        key=lambda i: (-final_results[i][0], final_results[i][1]))
    final_results = [final_results[i] for i in sort_order]
    scored_candidates = [scored_candidates[i] for i in sort_order]

    # ════════════════════════════════════════════════════════════════════════
    # ▼▼▼ VIVEK INTEGRATION POINT ▼▼▼
    #
    # Seema's scoring pipeline ends here.
    # Vivek — plug in your candidate analysis logic below.
    #
    # WHAT YOU HAVE:
    #   final_results   — list[(score, candidate_id, reasoning)]
    #                     Sorted best → worst by Seema's 5-dim formula.
    #
    #   candidate_data  — list[dict]  (top 5000 raw candidate dicts)
    #                     Each dict has: "candidate_id", "profile", "skills",
    #                     "career_history", "education", "certifications",
    #                     "redrob_signals", etc.
    #
    #   parsed_jd       — ParsedJD with: .required_skills, .preferred_skills,
    #                     .experience_min/max, .hidden_requirements, .role, etc.
    #
    # YOUR SCOPE:
    #   1. Candidate feature extraction (go deeper into candidate_data dicts)
    #   2. Hidden talent detection (signals in career/skills Seema didn't catch)
    #   3. Skill authenticity checks (endorsement vs duration vs proficiency)
    #   4. Re-score or adjust final_results with your candidate-level scores
    #
    # HOW TO PLUG IN:
    #   cand_lookup = {c["candidate_id"]: c for c in candidate_data}
    #   # Then loop over final_results, enrich/re-score as needed.
    #   # Keep format: list[(float, str, str)] sorted descending by score.
    #
    # EXAMPLE:
    #   from src.vivek_module import vivek_reranker
    #   final_results = vivek_reranker(final_results, candidate_data, parsed_jd)
    #
    # ════════════════════════════════════════════════════════════════════════

    # ════════════════════════════════════════════════════════════════════════
    # ▼▼▼ TEAMMATE-3 INTEGRATION POINT ▼▼▼
    #
    # After Seema's JD intelligence + Vivek's candidate intelligence,
    # you receive the combined ranked list.
    #
    # YOUR SCOPE:
    #   1. Risk assessment — flag high-risk candidates (job hopping, gaps, etc.)
    #   2. Explainability — enrich the reasoning string with risk/trust labels
    #   3. Dashboard — build visualization of rankings (can read submission.csv)
    #
    # WHAT YOU HAVE (same variables):
    #   final_results   — list[(score, candidate_id, reasoning)]
    #   candidate_data  — list[dict]  (raw candidate dicts)
    #   parsed_jd       — ParsedJD object
    #
    # EXAMPLE:
    #   from src.risk_module import assess_risk, enrich_reasoning
    #   final_results = assess_risk(final_results, candidate_data)
    #   final_results = enrich_reasoning(final_results, candidate_data)
    #
    # ════════════════════════════════════════════════════════════════════════
    print("\n=== DEBUG CANDIDATE DATA ===")
    print(type(candidate_data))
    print("Candidates:", len(candidate_data))

    if candidate_data:
        print(candidate_data[0])
    final_results = assess_risk(
    final_results,
    candidate_data
)
    elapsed_total = time.time() - start_time
    print(f"\n  Pass 2 complete in {time.time() - pass2_start:.1f}s")
    print(f"  Total pipeline time: {elapsed_total:.1f}s")

    # ---- Step 7: Write outputs ----
    # OUTPUT 2: ranked_candidates.csv (team deliverable — per-dimension scores)
    ranked_csv_path = output_dir / "ranked_candidates.csv"
    write_ranked_csv(scored_candidates, str(ranked_csv_path))

    # OUTPUT 3: submission.csv (challenge submission format)
    print(f"\n[Pipeline] Writing challenge submission to {output_path}...")
    write_submission(final_results, output_path)

    # Print top 10 preview
    print("\n[Pipeline] === TOP 10 CANDIDATES ===")
    for rank_num, (score, cid, reasoning) in enumerate(final_results[:10], 1):
        print(f"  #{rank_num:3d}  {cid}  score={score:.4f}  {reasoning}")

    print(f"\n[Pipeline] Done! {total_candidates} candidates ranked in {elapsed_total:.1f}s")
    print(f"\n  OUTPUTS:")
    print(f"    1. {jd_json_path}        <- Parsed JD (team deliverable)")
    print(f"    2. {ranked_csv_path}     <- Ranked candidates with all scores (team deliverable)")
    print(f"    3. {output_path}              <- Challenge submission (top 100)")
    return final_results


# ===========================================================================
# CLI
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="RedRob Intelligent Candidate Ranking Pipeline"
    )
    parser.add_argument(
        "--candidates", "-c",
        default=PIPELINE_CONFIG["candidates_file"],
        help="Path to candidates file (.jsonl or .json)"
    )
    parser.add_argument(
        "--out", "-o",
        default=PIPELINE_CONFIG["output_file"],
        help="Output CSV path"
    )
    parser.add_argument(
        "--jd", "-j",
        default=None,
        help="Path to custom JD text file (uses built-in JD if not provided)"
    )

    args = parser.parse_args()

    # Load custom JD if provided
    jd_text = None
    if args.jd:
        jd_path = Path(args.jd)
        if jd_path.exists():
            jd_text = jd_path.read_text(encoding="utf-8")
        else:
            print(f"WARNING: JD file not found: {args.jd}, using built-in JD")

    run_pipeline(args.candidates, args.out, jd_text)


if __name__ == "__main__":
    main()
