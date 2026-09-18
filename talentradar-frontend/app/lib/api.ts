import type { AnalyticsResponse, CandidateDetailResponse, CandidatesResponse } from './types'

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL ?? '/api'

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${baseURL}${path}`, {
    cache: 'no-store',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`API request failed: ${response.status} ${response.statusText} - ${text}`)
  }

  return response.json()
}

export async function getCandidates(q?: string): Promise<CandidatesResponse> {
  const url = q ? `/candidates?q=${encodeURIComponent(q)}` : '/candidates'
  return fetchJson<CandidatesResponse>(url)
}

export async function rankCandidates(jobDescription: string): Promise<any> {
  const response = await fetch(`${baseURL}/rank`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ job_description: jobDescription }),
  })
  
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`API request failed: ${response.status} ${response.statusText} - ${text}`)
  }
  
  return response.json()
}

export async function getCandidate(candidateId: string) {
  return fetchJson<CandidateDetailResponse>(`/candidates/${candidateId}`)
}

export async function getAnalytics() {
  return fetchJson<AnalyticsResponse>('/analytics')
}
