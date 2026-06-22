def assess_risk(final_results, candidate_data):
    candidate_lookup = {
        c["candidate_id"]: c
        for c in candidate_data
    }

    updated_results = []

    for score, cid, reasoning in final_results:
        candidate = candidate_lookup.get(cid, {})

        risk = "LOW"

        # Career history check
        jobs = candidate.get("career_history", [])

        if len(jobs) >= 4:
            risk = "HIGH"
        elif len(jobs) == 3:
            risk = "MEDIUM"

        # Profile completeness check
        signals = candidate.get("redrob_signals", {})
        completeness = signals.get("profile_completeness_score", 100)

        if completeness < 60:
            risk = "HIGH"

        reasoning = f"{reasoning} | Risk={risk}"

        updated_results.append(
            (score, cid, reasoning)
        )

    return updated_results