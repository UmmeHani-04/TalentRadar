export interface CandidateSummary {
  candidate_id: string
  rank: number
  score: number
  reasoning: string
  risk?: string
  semantic_score?: number
  experience_score?: number
  domain_score?: number
  momentum_score?: number
  hidden_talent_score?: number
  behavior_score?: number
  potential_score?: number
  authenticity_score?: number
  profile: {
    anonymized_name?: string
    headline?: string
    summary?: string
    location?: string
    years_of_experience?: number
    current_title?: string
    current_company?: string
    current_industry?: string
  }
  skills: Array<{ name: string } | string>
}

export interface CandidateDetail {
  candidate_id: string
  rank?: number
  score?: number
  reasoning?: string
  risk?: string
  semantic_score?: number
  experience_score?: number
  domain_score?: number
  momentum_score?: number
  hidden_talent_score?: number
  behavior_score?: number
  potential_score?: number
  authenticity_score?: number
  profile: {
    anonymized_name?: string
    headline?: string
    summary?: string
    location?: string
    years_of_experience?: number
    current_title?: string
    current_company?: string
    current_industry?: string
  }
  career_history: Array<Record<string, unknown>>
  skills: Array<{ name: string }>
  redrob_signals: Record<string, unknown>
  raw: Record<string, unknown>
}

export interface AnalyticsResponse {
  total_candidates: number
  average_score: number
  risk_distribution: Record<string, number>
  hidden_talent_count: number
  hidden_talent_ids: string[]
  skill_demand: Array<{ skill: string; demand: number; supply: number }>
  hiring_funnel: Array<{ stage: string; candidates: number }>
  experience_breakdown: Array<{ year: string; junior: number; mid: number; senior: number }>
  future_potential: Array<{ potential: string; percentage: number; fill: string }>
}

export type CandidateDetailResponse = CandidateDetail

export interface CandidatesResponse {
  results: CandidateSummary[]
  total_candidates: number
}
