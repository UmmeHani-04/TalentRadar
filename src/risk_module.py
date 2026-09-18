from src.config import RISK_CONFIG

def assess_risk(final_results, candidate_data):
    """Core Module 9: Risk Analysis.
    
    Identifies risk patterns (job hopping, inconsistent paths) and applies 
    a flat point deduction to the candidate's final score. Updates reasoning.
    """
    candidate_lookup = {c["candidate_id"]: c for c in candidate_data}
    updated_results = []

    for score, cid, reasoning in final_results:
        candidate = candidate_lookup.get(cid, {})
        
        penalty = 0.0
        risk_flags = []
        
        # 1. Job Hopping Check
        career = candidate.get("career_history", [])
        if career:
            durations = [job.get("duration_months", 0) for job in career]
            avg_tenure = sum(durations) / max(1, len(durations))
            
            # If avg tenure < 12 months across > 2 jobs
            if avg_tenure < 12 and len(career) >= 3:
                penalty += RISK_CONFIG["job_hopping_penalty"]
                risk_flags.append("Job Hopper")
                
        # 2. Inconsistent Path (e.g. Sales -> HR -> Engineer)
        # Using a simplified heuristic: if they have mostly non-tech skills but apply for AI
        skills = candidate.get("skills", [])
        if skills:
            tech_skills = ["python", "java", "sql", "aws", "machine learning", "react"]
            tech_count = sum(1 for s in skills if any(t in s.get("name", "").lower() for t in tech_skills))
            if len(skills) > 3 and tech_count == 0:
                penalty += RISK_CONFIG["inconsistent_path_penalty"]
                risk_flags.append("Inconsistent Path")
                
        # Calculate Risk Level
        risk_level = "Low"
        if penalty >= RISK_CONFIG["high_risk_threshold"]:
            risk_level = "High"
        elif penalty >= RISK_CONFIG["medium_risk_threshold"]:
            risk_level = "Medium"
            
        # Apply penalty (converting penalty scale 0-100 to 0-1 score scale)
        final_adjusted_score = score - (penalty / 100.0)
        final_adjusted_score = max(0.0, final_adjusted_score)
        
        # Append risk info to reasoning string
        if risk_flags:
            reasoning = f"{reasoning}\\n\\nRisk Level: {risk_level} ({', '.join(risk_flags)})"
        else:
            reasoning = f"{reasoning}\\n\\nRisk Level: {risk_level}"
            
        updated_results.append((final_adjusted_score, cid, reasoning))

    # Re-sort since scores changed
    sort_order = sorted(range(len(updated_results)), key=lambda i: (-updated_results[i][0], updated_results[i][1]))
    return [updated_results[i] for i in sort_order]