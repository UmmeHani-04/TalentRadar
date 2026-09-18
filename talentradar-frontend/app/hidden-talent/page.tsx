'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Sparkles, Brain, Zap, TrendingUp, Lock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { getAnalytics, getCandidates } from '@/app/lib/api'
import type { CandidateSummary, AnalyticsResponse } from '@/app/lib/types'

interface HiddenTalent {
  id: string
  name: string
  currentRole: string
  currentCompany: string
  matchConfidence: number
  hiddenMatchReason: string
  transferableSkills: string[]
  yearsExperience: number
  discoveryReason: string
  targetRole: string
  profileUrl?: string
}

const EMPTY_TALENTS: HiddenTalent[] = []

function mapCandidateToHiddenTalent(candidate: CandidateSummary): HiddenTalent {
  const skillNames = candidate.skills.map((s) => {
    if (typeof s === 'string') return s
    return s.name ?? 'Unknown Skill'
  })

  return {
    id: candidate.candidate_id,
    name: candidate.profile.anonymized_name ?? candidate.candidate_id,
    currentRole: candidate.profile.current_title ?? 'Professional',
    currentCompany: candidate.profile.current_company ?? candidate.profile.current_industry ?? 'Industry Expert',
    matchConfidence: Math.round(candidate.score),
    hiddenMatchReason: candidate.reasoning ?? 'Identified as hidden talent with transferable skills beyond standard keyword matching.',
    transferableSkills: skillNames.length > 0 ? skillNames.slice(0, 6) : ['Transferable Skills'],
    yearsExperience: candidate.profile.years_of_experience ?? 0,
    discoveryReason: `AI analysis identified transferable skills and high potential beyond exact job title matches. Risk level: ${candidate.risk ?? 'N/A'}.`,
    targetRole: candidate.profile.headline ?? 'Target Role',
  }
}

export default function HiddenTalentPage() {
  const router = useRouter()
  const [hiddenTalents, setHiddenTalents] = useState<HiddenTalent[]>([])
  const [selectedTalent, setSelectedTalent] = useState<HiddenTalent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalAnalyzed, setTotalAnalyzed] = useState(0)

  useEffect(() => {
    let active = true

    const loadData = async () => {
      try {
        // Fetch analytics to get hidden talent IDs, and all candidates
        const [analyticsData, candidatesData] = await Promise.all([
          getAnalytics(),
          getCandidates(),
        ])

        if (!active) return

        const hiddenIds = new Set(analyticsData.hidden_talent_ids ?? [])
        setTotalAnalyzed(analyticsData.total_candidates ?? 0)

        if (hiddenIds.size > 0) {
          // Filter candidates to only hidden talent
          const hiddenCandidates = candidatesData.results.filter(
            (c) => hiddenIds.has(c.candidate_id)
          )
          const mapped = hiddenCandidates.map(mapCandidateToHiddenTalent)
          if (mapped.length > 0) {
            setHiddenTalents(mapped)
            setSelectedTalent(mapped[0])
          } else {
            setHiddenTalents([])
            setSelectedTalent(null)
          }
        } else {
          // No hidden talent IDs from analytics — show top candidates as discovered talent
          const mapped = candidatesData.results.slice(0, 6).map(mapCandidateToHiddenTalent)
          if (mapped.length > 0) {
            setHiddenTalents(mapped)
            setSelectedTalent(mapped[0])
          } else {
            setHiddenTalents([])
            setSelectedTalent(null)
          }
        }
      } catch (err) {
        console.error('Failed to load hidden talent data:', err)
        if (active) {
          setError('Unable to load from backend. Showing sample data.')
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    loadData()
    return () => {
      active = false
    }
  }, [])

  const avgConfidence = hiddenTalents.length > 0
    ? Math.round(hiddenTalents.reduce((a, t) => a + t.matchConfidence, 0) / hiddenTalents.length)
    : 0

  return (
    <div className="min-h-screen bg-background text-foreground dark">
      {/* Header */}
      <header className="border-b border-border/40 bg-card/30 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <div className="hidden sm:block">
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent blur-lg opacity-75 rounded-lg" />
                  <div className="relative bg-gradient-to-r from-primary to-accent rounded-lg p-2">
                    <Brain className="w-5 h-5 text-primary-foreground" />
                  </div>
                </div>
                Hidden Talent Discovery
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-primary">AI-Powered</span>
            </div>
            {loading && (
              <span className="text-xs text-muted-foreground animate-pulse">Loading...</span>
            )}
            {error && (
              <span className="text-xs text-muted-foreground">{error}</span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="mb-12">
          <div className="glass rounded-2xl p-8 border-border/40 mb-8">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <h2 className="text-3xl font-bold mb-2 flex items-center gap-2">
                  <Zap className="w-6 h-6 text-accent" />
                  Discover Hidden Talent
                </h2>
                <p className="text-muted-foreground text-lg mb-4">
                  Beyond keywords and exact matches. Our AI identifies candidates with transferable skills who are ready to grow into your open roles.
                </p>
                <div className="flex flex-wrap gap-2">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-success/10 border border-success/20 text-sm">
                    <span className="w-2 h-2 rounded-full bg-success" />
                    {hiddenTalents.length} Hidden Talents Found
                  </div>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-sm">
                    <Sparkles className="w-3 h-3" />
                    AI Match Confidence
                  </div>
                </div>
              </div>
              <div className="hidden sm:block relative w-24 h-24">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-lg blur-xl" />
                <div className="relative bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg border border-primary/20 flex items-center justify-center h-full w-full">
                  <Brain className="w-12 h-12 text-primary/50 pulse-glow" />
                </div>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass rounded-lg p-4 border-border/40">
              <p className="text-sm text-muted-foreground mb-1">Avg Match Confidence</p>
              <p className="text-2xl font-bold">{avgConfidence}%</p>
            </div>
            <div className="glass rounded-lg p-4 border-border/40">
              <p className="text-sm text-muted-foreground mb-1">Candidates Analyzed</p>
              <p className="text-2xl font-bold">{totalAnalyzed > 0 ? totalAnalyzed : hiddenTalents.length}</p>
            </div>
            <div className="glass rounded-lg p-4 border-border/40">
              <p className="text-sm text-muted-foreground mb-1">Skill Transfer Potential</p>
              <p className="text-2xl font-bold">{avgConfidence > 0 ? Math.round(avgConfidence * 0.9) : 82}%</p>
            </div>
          </div>
        </div>

        {/* Candidates Grid + Detail */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Candidate Cards */}
          <div className="lg:col-span-1 space-y-4">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-accent" />
              Discovered Talent
            </h3>
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
              {hiddenTalents.map((talent) => (
                <button
                  key={talent.id}
                  onClick={() => setSelectedTalent(talent)}
                  className={`w-full text-left p-4 rounded-lg border transition-all duration-300 ${
                    selectedTalent?.id === talent.id
                      ? 'glass border-primary/40 bg-primary/5 glow'
                      : 'glass border-border/40 hover:border-primary/20 hover:bg-primary/5'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold">{talent.name}</p>
                      <p className="text-xs text-muted-foreground">{talent.currentRole}</p>
                    </div>
                    <div className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary/10 border border-primary/20">
                      <Sparkles className="w-3 h-3 text-primary" />
                      <span className="text-xs font-medium text-primary">{talent.matchConfidence}%</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">{talent.hiddenMatchReason}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Talent Detail */}
          {selectedTalent && (
            <div className="lg:col-span-2">
              <div className="space-y-6">
                {/* AI Badge */}
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-2xl blur-xl" />
                  <div className="relative glass rounded-2xl p-8 border-primary/20">
                    <div className="flex items-center justify-center gap-2 mb-6">
                      <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent blur-lg opacity-60 rounded-full" />
                        <div className="relative bg-gradient-to-r from-primary to-accent rounded-full p-3 pulse-glow">
                          <Brain className="w-6 h-6 text-white" />
                        </div>
                      </div>
                      <div className="text-center">
                        <p className="font-bold text-lg">Hidden Talent Detected</p>
                        <p className="text-xs text-muted-foreground">AI Confidence Score: {selectedTalent.matchConfidence}%</p>
                      </div>
                    </div>

                    {/* Confidence Meter */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Match Confidence</span>
                        <span className="text-2xl font-bold text-primary">{selectedTalent.matchConfidence}%</span>
                      </div>
                      <div className="w-full h-3 rounded-full bg-card/50 border border-border/40 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500 glow"
                          style={{ width: `${selectedTalent.matchConfidence}%` }}
                        />
                      </div>
                    </div>

                    {/* Candidate Info */}
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Name</p>
                        <p className="text-lg font-semibold">{selectedTalent.name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Years of Experience</p>
                        <p className="text-lg font-semibold">{selectedTalent.yearsExperience}+ years</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Current Role</p>
                        <p className="text-lg font-semibold">{selectedTalent.currentRole}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Company / Industry</p>
                        <p className="text-lg font-semibold text-accent">{selectedTalent.currentCompany}</p>
                      </div>
                    </div>

                    {/* Hidden Match Reason */}
                    <div className="mb-6 p-4 rounded-lg bg-card/50 border border-accent/20">
                      <h3 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-primary" />
                        Hidden Match Reason
                      </h3>
                      <p className="text-foreground/90 whitespace-pre-wrap">
                        {selectedTalent.hiddenMatchReason.replace(/\\n/g, '\n')}
                      </p>
                    </div>

                    {/* Why Discovered */}
                    <div className="mb-6 p-4 rounded-lg bg-card/50 border border-primary/20">
                      <p className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                        <Brain className="w-4 h-4 text-primary" />
                        Why Candidate Was Discovered
                      </p>
                      <p className="text-sm">{selectedTalent.discoveryReason}</p>
                    </div>

                    {/* Transferable Skills */}
                    <div>
                      <p className="text-sm text-muted-foreground mb-3 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-success" />
                        Transferable Skills
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {selectedTalent.transferableSkills.map((skill) => (
                          <div
                            key={skill}
                            className="px-3 py-1 rounded-full bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 text-sm font-medium text-primary"
                          >
                            {skill}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-8 flex gap-3">
                      <Button className="flex-1 bg-primary hover:bg-primary/90" onClick={() => router.push(`/candidates/${selectedTalent.id}`)}>
                        <Sparkles className="w-4 h-4 mr-2" />
                        View Full Profile
                      </Button>
                      <Button variant="outline" className="flex-1" onClick={() => window.location.href = `mailto:${selectedTalent.name.toLowerCase().replaceAll(' ', '.')}@example.com`}>
                        Send Message
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
