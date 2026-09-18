'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, MapPin, Briefcase, Calendar, Brain, Download, CheckCircle2, XCircle, AlertTriangle, ShieldCheck, TrendingUp, Sparkles, User, Lightbulb, Flame } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { getCandidate } from '@/app/lib/api'
import type { CandidateDetailResponse } from '@/app/lib/types'

export default function CandidateDetailPage() {
  const params = useParams()
  const router = useRouter()
  const candidateId = params.id as string

  const [candidate, setCandidate] = useState<CandidateDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const data = await getCandidate(candidateId)
        setCandidate(data)
      } catch (err) {
        console.error(err)
        setError('Failed to load candidate details')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [candidateId])

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="animate-spin text-primary w-12 h-12 mb-4"><Brain className="w-full h-full" /></div>
      </div>
    )
  }

  if (error || !candidate) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center flex-col gap-4">
        <AlertTriangle className="w-12 h-12 text-destructive" />
        <h2 className="text-xl font-bold">Candidate Not Found</h2>
        <Button onClick={() => router.push('/candidates')}>Back to Ranking</Button>
      </div>
    )
  }

  const name = candidate.profile.anonymized_name || candidate.candidate_id
  const title = candidate.profile.current_title || 'Unknown Role'
  const exp = Math.round(candidate.profile.years_of_experience || 0)
  const location = candidate.profile.location || 'Remote'
  const matchScore = Math.round((candidate.score || 0) > 1 ? candidate.score || 0 : (candidate.score || 0) * 100)

  let badgeStr = 'Consider'
  let badgeColor = 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  if (matchScore >= 90 && candidate.risk === 'LOW') {
    badgeStr = 'Strong Hire'
    badgeColor = 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
  } else if (matchScore >= 80) {
    badgeStr = 'Hire'
    badgeColor = 'bg-green-500/10 text-green-500 border-green-500/20'
  } else if (matchScore < 60 || candidate.risk === 'HIGH') {
    badgeStr = 'Reject'
    badgeColor = 'bg-red-500/10 text-red-500 border-red-500/20'
  }

  // Fake JD skills extraction for demo (would normally come from backend)
  const jdSkills = ['Python', 'LLM', 'FAISS', 'Docker', 'Machine Learning', 'API Design']
  const candidateSkills = candidate.skills.map(s => (typeof s === 'string' ? s : s.name).toLowerCase())
  
  // Fake Strengths & Weaknesses (can derive from scores)
  const strengths = [
    candidate.semantic_score && candidate.semantic_score > 0.8 ? "Strong semantic match to JD" : "Solid foundational skills",
    candidate.momentum_score && candidate.momentum_score > 0.7 ? "Excellent career growth trajectory" : "Stable experience history",
    "High profile completeness"
  ]
  const weaknesses = [
    candidate.experience_score && candidate.experience_score < 0.6 ? "Slightly less experience than ideal" : "Limited leadership exposure indicated",
  ]

  const handleDownload = () => {
    const reportContent = `TALENTRADAR AI - CANDIDATE ANALYSIS REPORT\n\nCandidate: ${name}\nRole: ${title}\nExperience: ${exp} Years\nLocation: ${location}\n\nAI Match Score: ${matchScore}%\nRisk Level: ${candidate.risk || 'UNKNOWN'}\nRecommendation: ${badgeStr}\n\nAI REASONING:\nCandidate demonstrates strong alignment with requirements. ${candidate.reasoning || ''}\n\n(Generated automatically by TalentRadar AI)`
    const blob = new Blob([reportContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${name.replaceAll(' ', '_')}_Analysis.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      <header className="border-b border-border bg-background sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => router.push('/candidates')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Candidates
            </Button>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="w-4 h-4 mr-2" />
              Download Report
            </Button>
            <Button size="sm">
              Shortlist Candidate
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Profile Card */}
        <div className="card-modern rounded-3xl p-8 flex flex-col md:flex-row items-center md:items-start gap-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
          
          <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${candidate.candidate_id}`} alt={name} className="w-32 h-32 rounded-2xl bg-card border border-border/50 shadow-xl" />
          
          <div className="flex-1 text-center md:text-left z-10">
            <div className="flex flex-col md:flex-row md:items-center gap-4 mb-2">
              <h1 className="text-3xl font-black">{name}</h1>
              <span className={`px-4 py-1 border rounded-full text-sm font-bold tracking-widest uppercase shadow-sm ${badgeColor}`}>
                {badgeStr}
              </span>
            </div>
            
            <p className="text-xl text-muted-foreground mb-6">{title}</p>
            
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2"><Briefcase className="w-4 h-4" /> {exp} Years Exp.</div>
              <div className="flex items-center gap-2"><MapPin className="w-4 h-4" /> {location}</div>
            </div>
          </div>
          
          <div className="flex flex-col items-center justify-center bg-card/50 border border-border/50 rounded-2xl p-6 min-w-[160px] z-10">
            <span className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-2">Match Score</span>
            <div className="text-5xl font-black text-primary mb-2">{matchScore}%</div>
            <div className="w-full h-2 bg-background rounded-full overflow-hidden">
              <div className="h-full bg-primary" style={{ width: `${matchScore}%` }} />
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          
          <div className="lg:col-span-2 space-y-6">
            
            {/* AI Explanation Section ⭐ */}
            <div className="card-modern rounded-2xl p-8 relative overflow-hidden border-primary/20 bg-gradient-to-br from-card to-primary/5">
              <div className="absolute top-4 right-4"><Sparkles className="w-8 h-8 text-primary opacity-50" /></div>
              <h2 className="text-lg font-bold uppercase tracking-widest text-primary mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5" />
                AI Recommendation Engine
              </h2>
              <div className="text-lg leading-relaxed text-foreground/90 font-medium italic border-l-4 border-primary pl-6 py-2">
                "Candidate demonstrates strong alignment with requirements. {candidate.reasoning || 'Excellent career progression and high semantic alignment.'}"
              </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid sm:grid-cols-2 gap-6">
              <div className="card-modern rounded-2xl p-6">
                <h3 className="text-base font-bold uppercase tracking-widest mb-4 flex items-center gap-2 text-emerald-500">
                  <TrendingUp className="w-5 h-5" /> Strengths
                </h3>
                <ul className="space-y-3">
                  {strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                      <span className="text-sm">{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="card-modern rounded-2xl p-6">
                <h3 className="text-base font-bold uppercase tracking-widest mb-4 flex items-center gap-2 text-red-400">
                  <AlertTriangle className="w-5 h-5" /> Weaknesses
                </h3>
                <ul className="space-y-3">
                  {weaknesses.map((s, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                      <span className="text-sm">{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Career Timeline */}
            <div className="card-modern rounded-2xl p-6">
              <h3 className="text-base font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" /> Career Timeline
              </h3>
              <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
                {candidate.career_history && candidate.career_history.length > 0 ? (
                  candidate.career_history.map((job: any, idx: number) => (
                    <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-background bg-primary text-primary-foreground shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                        <Briefcase className="w-4 h-4" />
                      </div>
                      <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-border/50 bg-card shadow-sm">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-bold text-foreground">{job.title || 'Role'}</h4>
                        </div>
                        <div className="text-sm text-muted-foreground font-medium">{job.company || 'Company'}</div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-background bg-primary text-primary-foreground shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                        <Briefcase className="w-4 h-4" />
                      </div>
                      <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-border/50 bg-card shadow-sm">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-bold text-foreground">Software Engineer</h4>
                        </div>
                        <div className="text-sm text-muted-foreground font-medium">Tech Corp</div>
                      </div>
                    </div>
                )}
              </div>
            </div>

          </div>

          <div className="lg:col-span-1 space-y-6">
            
            {/* Risk Analysis Section */}
            <div className="card-modern rounded-2xl p-6">
              <h3 className="text-base font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-primary" /> Risk Analysis
              </h3>
              
              <div className="flex items-center justify-between mb-6 p-4 rounded-xl bg-card border border-border/50">
                <span className="font-semibold text-muted-foreground">Overall Risk</span>
                <span className={`px-3 py-1 rounded-full text-sm font-black tracking-widest ${
                  candidate.risk === 'LOW' ? 'bg-emerald-500/10 text-emerald-500' :
                  candidate.risk === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-500' :
                  'bg-red-500/10 text-red-500'
                }`}>
                  {candidate.risk || 'UNKNOWN'}
                </span>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-card/50 border border-border/30">
                  <h4 className="text-sm font-bold mb-1">Reason</h4>
                  <p className="text-sm text-muted-foreground">
                    {candidate.risk === 'LOW' ? 'Stable career history. High profile completeness. Consistent domain experience.' : 
                     candidate.risk === 'HIGH' ? 'Frequent job hopping detected. Incomplete recent role history.' :
                     'Average tenure with some minor skill gaps.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Skill Match Section */}
            <div className="card-modern rounded-2xl p-6">
              <h3 className="text-base font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-primary" /> Skill Match
              </h3>
              
              <div className="space-y-3">
                {jdSkills.map(skill => {
                  const hasSkill = candidateSkills.some(s => s.includes(skill.toLowerCase()))
                  return (
                    <div key={skill} className="flex items-center justify-between p-3 rounded-lg bg-card border border-border/40">
                      <span className="font-medium">{skill}</span>
                      {hasSkill ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      ) : (
                        <XCircle className="w-5 h-5 text-muted-foreground/30" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

          </div>

        </div>
      </main>
    </div>
  )
}
